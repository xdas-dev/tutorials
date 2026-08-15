# Xdas tutorials — rewrite against `feature/better-atoms`

Two things are in here: what I **already changed**, and what I **propose** to
do next.

**Status:** eight notebooks, all executing end to end with zero failing cells.
01–05 are the existing ones rewritten; 06, 07 and 08 are new. The only part
of your original request I could not finish is putting the DAS channels into
the GaMMA association, which needs the cable geometry — see section 5.

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

The cable never enters the association, which makes it an independent check:
the median S−P over 1743 channels implies a hypocentral distance of **32 km**
against the network's **36 km** depth. The fiber sits almost above the source,
so those two numbers are measuring the same thing, and they agree about as
well as an 8-pick location with two constant velocities can.

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

1. **Cable geometry — the one real blocker.** Lat/lon per channel for at least
   `SER/N`. Both notebook 05 and notebook 07 already read
   `data/geometry/SER_N.csv` with columns `distance,latitude,longitude`, and
   both degrade gracefully without it (05 falls back to a synthetic straight
   line and says so; 07 prints what it would do). Drop the file in and the
   DAS channels can join the association, which is the last piece of what you
   asked for.
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
