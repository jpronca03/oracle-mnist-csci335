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

You may also need to install numpy

To run, enter into the src directory and run the following command

```bash
py train_pytorch.py --lr 0.1 --epochs 15 --net Net2 --data-dir ../data/oracle/
```
