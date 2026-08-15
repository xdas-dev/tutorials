"""Set up the tutorial series in one command:

    uv run install.py

`uv run` installs the dependencies listed in pyproject.toml before this script
starts; the script then fetches the data:

  * the DAS samples from Zenodo, unzipped into `data/`,
  * the seismological waveforms used from notebook 05 onwards, saved as one
    miniSEED file per station in `data/stations/`, next to the inventory,
  * the pretrained PhaseNet weights, cached in ~/.seisbench.

After it, the notebooks run offline.

Every step is skipped if it is already done, and an interrupted download is
resumed where it stopped, so re-running is cheap. Pass --force to start over.
"""

import argparse
import shutil
import sys
import time
import urllib.error
import urllib.request
import warnings
import zipfile
from pathlib import Path

# Report as the work happens, even when the output is piped to a file.
sys.stdout.reconfigure(line_buffering=True)

ROOT = Path(__file__).parent
DATA = ROOT / "data"
STATIONS = DATA / "stations"
OUTPUTS = ROOT / "outputs"

DATA_URL = "https://zenodo.org/records/11212055/files/data.zip"
DATA_ZIP = ROOT / "data.zip"
# What the archive unpacks to. Used to tell "already downloaded" from "not yet".
DATA_DIRS = ("ntp_sync", "gps_multiacq", "gps_multicable")

# The window and the region of notebook 05: an offshore Coquimbo earthquake,
# recorded by the permanent stations around the cable.
STATIONS_START = "2023-11-03T12:25:30"
STATIONS_END = "2023-11-03T12:28:30"
STATIONS_BBOX = {
    "minlatitude": -32.8,
    "maxlatitude": -29.2,
    "minlongitude": -72.5,
    "maxlongitude": -69.8,
}
STATIONS_CHANNEL = "HH?"

# The pretrained picker of notebooks 03 and 05. Cached in ~/.seisbench.
MODEL = "diting"


def human(size):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(size) < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def download(url, dest):
    """Download `url` to `dest`, resuming a partial file when the server allows."""
    done = dest.stat().st_size if dest.exists() else 0
    request = urllib.request.Request(url)
    if done:
        request.add_header("Range", f"bytes={done}-")

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as error:
        if error.code == 416:  # asked past the end: the file is already whole
            print(f"{dest.name} is already fully downloaded")
            return
        raise

    with response:
        if done and response.status != 206:  # no resume, start over
            done = 0
        total = int(response.headers.get("Content-Length", 0)) + done
        if done:
            print(f"resuming at {human(done)} of {human(total)}")
        else:
            print(f"downloading {human(total)} from {url}")

        start, resumed = time.monotonic(), done
        with open(dest, "ab" if done else "wb") as file:
            while chunk := response.read(1 << 20):
                file.write(chunk)
                done += len(chunk)
                rate = (done - resumed) / max(time.monotonic() - start, 1e-6)
                percent = f"{100 * done / total:.1f}%, " if total else ""
                print(
                    f"\r  {human(done)} / {human(total) if total else '?'}"
                    f"  ({percent}{human(rate)}/s)",
                    end="",
                    flush=True,
                )
    print()

    if total and dest.stat().st_size != total:
        raise RuntimeError(
            f"{dest.name} is {human(dest.stat().st_size)}, expected {human(total)}. "
            "Re-run to resume."
        )


def fetch_data(force):
    """Download and unzip the DAS samples."""
    if not force and all((DATA / name).is_dir() for name in DATA_DIRS):
        print(f"data: already in {DATA}, skipping")
        return

    if force and DATA_ZIP.exists():
        DATA_ZIP.unlink()

    free = shutil.disk_usage(ROOT).free
    if free < 12 * 1024**3:
        print(f"warning: only {human(free)} free, the archive needs ~8 GB unpacked")

    download(DATA_URL, DATA_ZIP)

    print(f"unzipping into {DATA} (a few minutes)")
    try:
        with zipfile.ZipFile(DATA_ZIP) as archive:
            members = archive.infolist()
            total = max(sum(member.file_size for member in members), 1)
            done = 0
            for member in members:
                archive.extract(member, ROOT)
                done += member.file_size
                print(
                    f"\r  {human(done)} / {human(total)}  ({100 * done / total:.1f}%)",
                    end="",
                    flush=True,
                )
        print()
    except zipfile.BadZipFile:
        # Most often a data.zip left over from something else: resuming onto it
        # produces a file of the right size whose contents do not line up.
        DATA_ZIP.unlink()
        raise RuntimeError(
            f"{DATA_ZIP.name} was not a valid archive, so it has been deleted. "
            "Re-run to download it again."
        ) from None
    DATA_ZIP.unlink()

    missing = [name for name in DATA_DIRS if not (DATA / name).is_dir()]
    if missing:
        raise RuntimeError(f"the archive did not provide {missing}")
    print(f"data: unpacked into {DATA}")


def fetch_stations(force):
    """Fetch the seismological waveforms, one miniSEED file per station."""
    inventory_path = STATIONS / "stations.xml"
    # One file per station, named NET.STA.mseed. The single-file `stations.mseed`
    # that older versions of the tutorial shipped does not count.
    per_station = [
        path for path in STATIONS.glob("*.mseed") if path.stem.count(".") == 1
    ]
    if not force and inventory_path.exists() and per_station:
        print(f"stations: {len(per_station)} already in {STATIONS}, skipping")
        return

    from obspy import UTCDateTime
    from obspy.clients.fdsn import Client

    start, end = UTCDateTime(STATIONS_START), UTCDateTime(STATIONS_END)
    print(f"stations: querying EarthScope for {start} - {end}")

    client = Client("EARTHSCOPE", timeout=120)
    inventory = client.get_stations(
        starttime=start,
        endtime=end,
        level="channel",
        channel=STATIONS_CHANNEL,
        **STATIONS_BBOX,
    )
    bulk = [
        (network.code, station.code, "*", STATIONS_CHANNEL, start, end)
        for network in inventory
        for station in network
    ]
    stream = client.get_waveforms_bulk(bulk)
    print(f"  {len(stream)} traces fetched")

    STATIONS.mkdir(parents=True, exist_ok=True)
    if force:
        for stale in STATIONS.glob("*.mseed"):
            stale.unlink()

    # One file per station, all its components together. The traces are written
    # as they came: notebook 05 starts from their raw, slightly misaligned
    # start times.
    codes = sorted({(trace.stats.network, trace.stats.station) for trace in stream})
    for network, station in codes:
        traces = stream.select(network=network, station=station)
        path = STATIONS / f"{network}.{station}.mseed"
        traces.write(str(path), format="MSEED")
        print(f"  {path.name}: {len(traces)} traces, {human(path.stat().st_size)}")

    inventory.write(str(inventory_path), format="STATIONXML")

    legacy = STATIONS / "stations.mseed"
    if legacy.exists():  # superseded, and notebook 05 would read it twice
        legacy.unlink()
        print(f"  removed {legacy.name}, the old single-file copy")

    print(f"stations: {len(codes)} stations in {STATIONS}")


def fetch_model(force):
    """Cache the pretrained picker, so that nothing is downloaded while picking."""
    print("model: loading seisbench, which imports torch and takes a few seconds")
    with warnings.catch_warnings():
        # seisbench 0.12.3 leaves an unescaped '\m' in one of its docstrings
        warnings.simplefilter("ignore", SyntaxWarning)
        import seisbench
        from seisbench.models import PhaseNet

    cache = Path(seisbench.cache_root) / "models"
    if not force and any(cache.rglob(f"{MODEL}.pt*")):
        print(f"model: {MODEL} already in {cache}, skipping")
        return

    print(f"model: fetching the {MODEL} weights of PhaseNet")
    try:
        PhaseNet.from_pretrained(MODEL, force=force)
    except Exception as error:  # noqa: BLE001 -- offline, or the server is down
        print(f"warning: could not fetch the weights ({type(error).__name__})")
        print("         notebooks 03 and 05 will fetch them the first time they pick")
        return
    print(f"model: cached in {cache}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="download again even if already there"
    )
    args = parser.parse_args()

    fetch_data(args.force)
    fetch_stations(args.force)
    fetch_model(args.force)
    OUTPUTS.mkdir(exist_ok=True)

    print("\nready. Start the notebooks with:\n\n    uv run jupyter lab\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ninterrupted -- re-run to pick up where it stopped")
        sys.exit(130)
