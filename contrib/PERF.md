# Measure some performance for greater glory

```
pip install snakeviz pycallgraph
```

Then:
```
python -m cProfile -o benchmarch_prop.prof perf.py
snakeviz benchmarch_prop.prof
```
