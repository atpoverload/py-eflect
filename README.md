# python implementation of `eflect`

An implementation of [`eflect`](https://github.com/timurbey/eflect.git) for python.

This tool can be run using a file or a code snippet

```bash
python3 eflect -f path/to/file.py
python3 eflect -c 'import numpy as np; np.arange(10**9)'
```

and produces a directory called `data` that contains the collected samples and the energy footprint produced from the samples.
