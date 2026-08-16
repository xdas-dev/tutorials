# Xdas tutorials — rewrite against `feature/better-atoms`

Two things are in here: what I **already changed**, and what I **propose** to
do next.

**Status:** eight notebooks. 01–05 are the existing ones rewritten; 06, 07
and 08 are new. The DAS-into-GaMMA piece that section 5 originally flagged
as blocked on cable geometry is now built. Two unrelated regressions surfaced
on the `xdas` `dev` branch while re-running everything against the currently
pinned commit — `xd.decimate` gone, and the atom-composition-vs-monolithic
equivalence broken in notebook 03 — see section 6, items 5–6; notebook 03
currently has three failing cells because of the second one.

---

## 1. The syntax pass — done

All five notebooks were rewritten against `feature/better-atoms` (0.2.9.dev0)
and re-executed end to end. Zero failing cells.

| # | Notebook | What changed |
|---|---|---|
| 01 | timing issues | `delta` is now the **jump**, so the prose numbers changed: the two NTP seams are a **1 ms gap** and an **11 ms overlap**, not "9 ms" and "−3 ms". The `fp must be strictly increasing` demo is **gone** — an overlapping axis no longer raises, it warns and slices ~5× slower. Added a pointer to `xd.trim_overlaps`. |
| 02 | collections | `xs.get_sampling_interval` → `xd.get_sampling_interval`. Added `select()` with wildcards, `query()`, and the new `KeyError` on a level name that does not exist. Cut the "setting new elements" section (it only showed that a dict is a dict). |
| 03 | processing | The whole `xdas.signal` layer → the physical-unit vocabulary. `decimate(da, 16, ftype="fir")` → `decimate(da, 1/(16*dx))`, a **target rate**. Added `xd.filter(da, (1.0, 10.0))` in Hz. `xdas.fft` → `xd.fft`. Cut the `parallel=` tour. |
| 04 | atoms | The big one. `Sequential`/`Partial`/`LFilter` → `...`-seeded functions composed with `>>`. The `DataArrayLoader`+`DataArrayWriter`+`xp.process` triple → `pipeline.process(source, out=..., chunks=...)`. The `MLPicker`+`ResamplePoly`+`Trigger` chain → `xd.pick(da, model)`. Added `assert_chunk_invariant` and per-phase thresholds. **Roughly half the notebook was mechanism that the new API absorbs.** |
| 05 | coordinates | Added the three coordinate kinds, and the regularity story (`isregular`, `to_regular`) — including the `FutureWarning` you get from a hand-built coordinate, which turns a wart into the lesson. Geometry now loads from `data/geometry/SER_N.csv` with a synthetic fallback. |

### The one thing I removed rather than fixed

`da.sel(station=[...])` on a **non-dimensional** string coordinate raises
`IndexError`, and after `swap_dims` a list selection raises `TypeError`. The
0.2.9 notes say string/categorical `sel` works, so either the note is broader
than the feature or this path was missed. I cut the cell instead of working
around it — see section 6.

---

## 2. What I propose to cut

Beyond what is already gone, these read as filler now:

- **The `DataMapping` / `DataSequence` explanation in 02.** Two sentences, not
  a section. The repr teaches it faster than prose does.
- **The three-scenario framing of 02.** Scenario 2 ("a catalog of events") is
  really just "you can build a collection by hand", and it is a better fit as
  a short cell inside the GaMMA notebook, where the catalog is real.
- **The FK diagram in 03.** It is beautiful and it is also the one cell nobody
  learns anything transferable from — it teaches `fft`, which is a one-liner.
  Keep it, but as the *last* cell, flagged as a showcase rather than a step.
- **`process()` returning a value in 04.** Now that the sink is inferred, the
  interesting demo is `out="dir"` and `out="picks.csv"`. Running to memory is
  the special case, not the lesson.

---

## 3. The three new notebooks (built)

I appended rather than renumbered, so nothing existing moved.

### 06 — DAS next to seismological stations

- 7 stations of network `C1` around the cable, fetched from EarthScope FDSN
  **at run time** (you chose "nothing new, use FDSN on the fly" — it works, I
  verified from this machine), with a 560 kB copy in `data/stations/` as an
  offline fallback;
- opened with `engine="obspy"` → the `network/station/location/channel` tree;
- `xd.stack(dc, "channel", join="inner")` → one `(channel, time)` array per
  station;
- then the *same* `PhaseNet` model and the *same* `xd.pick(...)` call as the
  DAS.

That last point is why the notebook earns its place: the pipeline does not
change when the instrument does.

### 07 — From picks to a catalog with GaMMA

Station picks → `gamma.utils.association` → **one located event**:
`2023-11-03T12:26:49.75`, `-29.979 / -71.515`, depth 36 km, 8 picks. Neither
the USGS nor the EMSC catalog has anything at that time and place, so the
notebook genuinely builds a catalog rather than rediscovering one.

It then does the thing tutorials usually skip: predicts every arrival from
the location and shows the residuals. Most are a few tenths of a second; the
two enormous ones are `VA06`'s false picks at 287 km, which GaMMA discarded —
a much better lesson about what an associator is *for* than any amount of
prose.

The cable starts as an independent check: the median S−P over the picked
channels implies a hypocentral distance close to the network's depth. The
fiber sits almost above the source, so those two numbers are measuring the
same thing, and they agree about as well as an 8-pick location with two
constant velocities can. It then stops being just a witness — see the update
in section 5.1 — once real geometry lets its channels join the association
as stations in their own right.

### 08 — Manual picking with xpick

A full round trip, verified: PhaseNet picks → `POST /api/import` (one horizon
per phase) → correct them in the browser → `GET /api/export` → back into
pandas. The export **densifies**, so ~79 hand-placed vertices come back as
1941 per-channel picks, carrying `horizon`, `annotator` and `status` columns —
which is what makes the output a dataset rather than a pile of points.

**Caveat**: xpick's own `README.md` is stale — it still documents the Bokeh v1
app, not the current FastAPI/Vite one. Worth fixing before the tutorial points
at it.

---

## 4. Proposed structure (not applied)

The current order interleaves "how the object works" (03, 05) with "how to
scale it" (04). I would group them — but this renumbers files, so I left it
for you to approve:

```
Part I — Getting data in
  01  Linking files, and timing that lies          (was 01)
  02  Collections: many cables, many acquisitions  (was 02)

Part II — How a DataArray works
  03  Exploration and processing                   (was 03)
  04  Coordinates                                  (was 05, moved up)

Part III — Scale
  05  Atoms, chunking and massive processing       (was 04, moved down)
  06  Streaming and real time                      (would be new)

Part IV — Seismology, end to end
  07  DAS next to seismological stations           (built as 06)
  08  From picks to a catalog with GaMMA           (built as 07)
  09  Manual picking with xpick                    (built as 08)
```

Dependency-wise the move is free: coordinates needs only
`outputs/singlecable.nc`, and atoms needs `outputs/event.nc`.

**The one notebook I did not build** is *Streaming and real time*. 0.2.9 has
real streaming and no tutorial covers it: `xd.watch(dir)` as a source, a
ZeroMQ address at either end, `wait_until_subscribed()` so the example is not
a `sleep` and a prayer. Say the word and I will add it; it is the least
connected to the rest, so it is also the easiest to drop.

---

## 5. What I need from you

1. ~~**Cable geometry — the one real blocker.**~~ **Resolved, and used.**
   `install.py` fetches `CCN_N.csv`, `SER_N.csv` and `SER_S.csv` into
   `data/geometry/` automatically (`fetch_geometry`, wired into `main()`).
   The source is the figure data bundled in the companion paper's
   `codes.zip` (Baillet et al., 2025, JGR, doi:10.1029/2025JB031565, archived
   at https://zenodo.org/records/15849254) — that zip is 3.3 GB, but the
   geometry CSVs inside it are pulled out directly with HTTP range requests
   (`fetch_zip_member`), so nothing close to the full archive is downloaded.

   Real cable lengths turned out to be ~153 km (CCN/N, SER/S) and ~102 km
   (SER/N) — `SER_N.csv` stops at 102 km, short of the interrogator's 153 km
   range, and the first ~4.6 km repeats one coordinate (fiber coiled at the
   shore station). Both are now handled rather than clamped: notebook 01
   attaches `latitude`/`longitude` to every cable **at consolidation**
   (`with_geometry`, right before `to_netcdf`), interpolating with
   `left=right=np.nan` instead of `np.interp`'s default clamp, so channels
   past the surveyed length are honestly `NaN` rather than silently pinned to
   the last sample. `outputs/singlecable.nc` and `multicable.nc` now carry
   the coordinate, so nothing downstream reloads or reinterpolates the CSV.

   Notebook 04's "Adding a coordinate" section changed to match: it shows
   what already arrived with the file, explains the `NaN` tail and the
   coiled-cable ties, then trims to the surveyed/uncoiled stretch
   (`isel(distance=slice(300, 6660))`) before the `swap_dims` /
   latitude-`sel` demo, which needs a monotonic axis and would silently break
   on the untrimmed real data. The old synthetic-fallback branch
   (`except FileNotFoundError: ... straight cable`) is gone — the file always
   exists now.

   Notebook 06's "Putting the fiber into the association" section is built:
   `outputs/singlecable.nc`'s attached geometry is matched to whichever
   channels the picker fired on (174 of 202 in the current run — the other 28
   sit past the surveyed 102 km and are dropped), stacked onto the seismic
   stations/picks tables, and re-associated. This surfaces a few spurious
   clusters sitting right at `min_picks_per_eq` — a real lesson about
   per-channel picks, not a bug — sorted out by `gamma_score`, which lands on
   the same origin as the network-only catalog with dozens of times more
   picks and a depth that moves (expected: an 8-pick, two-velocity fit was
   never going to pin it exactly).

   `CCN_N.csv` (unused, full 153 km) could still bring in the second cable
   for azimuthal coverage — not done here since it changes what the notebook
   narrates, left for you to decide.
2. **Whether to apply the renumbering in section 4**, and whether you want the
   streaming notebook.
3. **Which cuts in section 2 you accept.**

### On the data package

I already implemented the offline fallback rather than only recommending it:
`data/stations/` holds 486 kB of miniSEED and 76 kB of StationXML — the exact
output of the live FDSN call, so the notebook tells the same story either way.
Both belong in the new `data.zip`, along with the geometry once it exists.

One network dependency has **no** fallback: `seisbench` downloads its
pretrained weights on first use. The README now says so.

---

## 6. Things I hit in xdas (reporting, not fixing)

All four are on `feature/better-atoms` as of `b32b30d`. I have **not** touched
the xdas repo.

1. **`Annotate.gather` cannot join.** It calls
   `stack(mapping, level, tolerance=self.tolerance)` with no `join`
   (`xdas/atoms/ml.py:893`). Real FDSN channels of one station routinely
   differ by a sample in length, so `xd.pick(dc, model)` on a network tree —
   the headline of the picking section in the release notes — raises
   `ValueError: ... pass join='inner' or join='outer'`, and there is no way to
   pass one. Workaround in the notebook: `xd.stack(dc, "channel",
   join="inner")` first, then pick. A `join` argument on `Annotate`/`Picker`
   would close it.

2. **`stack(..., tolerance=)` does not snap a sub-sample phase offset.** The
   three components of `C1.BO01` start 1 µs apart (others by up to 8 ms).
   `tolerance` appears to bound sampling-*interval* jitter, not a start-time
   offset, so `join="inner"` reports "the leaves share no coordinate value"
   however large the tolerance. Workaround: snap `tr.stats.starttime` onto the
   sampling grid in obspy before handing the stream over.

3. **String-coordinate `sel`** — as in section 1.

4. **A numpy `DeprecationWarning` leaks from `sel`**: "The 'generic' unit for
   NumPy timedelta is deprecated". It fires on an ordinary
   `da.sel(time=slice("...", "..."))` and will become an error. Cosmetic today,
   noisy in a tutorial.

5. **`xd.decimate` is gone.** It existed when notebook 04's decimation cell
   was written (row 22 of the table above) but is absent from the `dev`
   branch commit now pinned in `uv.lock` (`0567b4e`) — not renamed within
   `xd.signal` either, which still has the old `decimate(da, q, ...)` taking
   an integer factor, not a target rate. I patched the one cell that uses it
   to `xd.resample(da, down=16, dim="distance")`, which is the closest
   current equivalent, but did not go looking for other cells that might
   depend on the same entry point.

6. **`atomic.equals(monolithic)` and its two siblings fail in notebook 03**
   (`xd.resample(..., interval=250, snap=True) >> xd.filter(..., ftype="iir",
   ...)` composed via `>>` vs. called directly) — the atom/pipeline path and
   the monolithic call no longer agree bit-for-bit on the pinned commit,
   which is the exact property notebook 03 exists to demonstrate. I left the
   three cells failing rather than "fixing" the assertion, since I do not
   know whether the atom composition or the monolithic call is now the wrong
   one. `xd.testing.assert_chunk_invariant` two cells later still passes, so
   this is specifically about `>>`-composition vs. a direct call, not
   chunking. Ran with `jupyter execute --allow-errors` to still get real
   `outputs/picks.csv` out of the later, independent picking cells.
