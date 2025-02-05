# NÉE Invoice Automation

# Process

- Step 1: save the `physical orders report.xlsx` in the `data` folder
- Step 2: run app.py via `uv run app.py`

##### Miscellaneous

###### `weasyprint`

- raises errors for libraries not being installed.
  **error**
  `OSError: cannot load library 'libgobject-2.0-0': dlopen(libgobject-2.0-0,
0x0002): tried: 'libgobject-2.0-0' (no such file),
'/System/Volumes/Preboot/Cryptexes/OSlibgobject-2.0-0' (no such file),
'/usr/lib/libgobject-2.0-0' (no such file, not in dyld cache),
'libgobject-2.0-0' (no such file).  Additionally, ctypes.util.find_library() did
not manage to locate a library called 'libgobject-2.0-0'`

**solution: manually create symlinks**
(StackOverflow: gobject-2.0-0 not able to load on macbook)[https://stackoverflow.com/questions/69097224/gobject-2-0-0-not-able-to-load-on-macbook]
