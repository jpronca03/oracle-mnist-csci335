# Instructions to run

See python-packages.txt for what package versions to set up your environment with.

To run, enter into the src directory and run the following command

```bash
python3 train_pytorch.py --lr 0.1 --epochs 15 --data-dir ../data/oracle/
```

The size of the two kernels can be modified with the `k1` and `k2` arguments:
```bash
python3 train_pytorch.py --lr 0.1 --epochs 15 --k1 original --k2 large --data-dir ../data/oracle/
```

The dropout rate can be modified with the `dropout` argument:
```bash
python3 train_pytorch.py --lr 0.1 --epochs 15 --dropout 0.1 --data-dir ../data/oracle/
```

Example command to graph the results of each class:
```bash
python3 grapher.py --in-file ./results/model_class_accuracies.csv --out-file ./plots/class_acc.png --graph classes
```