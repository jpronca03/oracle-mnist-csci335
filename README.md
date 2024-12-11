# Instructions to run

Once the repository is cloned, you can use an environment with the same packages as `ml2024`, but will have to install two additional modules.

First is torch

```bash
pip install torch
```

Second is torchvision

```bash
pip install torchvision
```

For other environments, you may also need to install numpy

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
