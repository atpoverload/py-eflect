# python implementation of `eflect`

An implementation of [`eflect`](https://github.com/timurbey/eflect.git) for python.

## running

First, you'll need to build the protos:

```bash
sudo apt-get install protoc && make protos && make smoke_test
```

Once built, this tool can be run on a file or a code snippet:

```bash
mkdir data && sudo python3 eflect -f path/to/file.py --data data
mkdir data && sudo python3 eflect -c 'import numpy as np; np.arange(10**9)' --data data
```

this produces a directory called `data` that contains the collected samples as a proto binary and the energy footprint produced from the samples as a tall csv.
