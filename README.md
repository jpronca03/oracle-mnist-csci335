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
python3 train_pytorch.py --lr 0.1 --epochs 15 --net Net2 --data-dir ../data/oracle/
```
Expected Output:
```bash
The size of train set: 27222
The size of t10k set: 3000
Train Epoch: 1 [0/27222 (0%)]   Loss: 2.305176
Train Epoch: 1 [640/27222 (2%)] Loss: 2.179815
Train Epoch: 1 [1280/27222 (5%)]        Loss: 1.956573
Train Epoch: 1 [1920/27222 (7%)]        Loss: 1.891249
Train Epoch: 1 [2560/27222 (9%)]        Loss: 1.812013
Train Epoch: 1 [3200/27222 (12%)]       Loss: 1.615749
Train Epoch: 1 [3840/27222 (14%)]       Loss: 1.511860
Train Epoch: 1 [4480/27222 (16%)]       Loss: 1.371267
Train Epoch: 1 [5120/27222 (19%)]       Loss: 1.466893
Train Epoch: 1 [5760/27222 (21%)]       Loss: 1.409430
Train Epoch: 1 [6400/27222 (24%)]       Loss: 1.171674
Train Epoch: 1 [7040/27222 (26%)]       Loss: 0.995179
Train Epoch: 1 [7680/27222 (28%)]       Loss: 1.097204
Train Epoch: 1 [8320/27222 (31%)]       Loss: 0.972762
Train Epoch: 1 [8960/27222 (33%)]       Loss: 0.832347
Train Epoch: 1 [9600/27222 (35%)]       Loss: 0.864178
Train Epoch: 1 [10240/27222 (38%)]      Loss: 0.982208
Train Epoch: 1 [10880/27222 (40%)]      Loss: 0.843341
Train Epoch: 1 [11520/27222 (42%)]      Loss: 0.822641
Train Epoch: 1 [12160/27222 (45%)]      Loss: 0.512926
Train Epoch: 1 [12800/27222 (47%)]      Loss: 0.790022
Train Epoch: 1 [13440/27222 (49%)]      Loss: 0.651920
Train Epoch: 1 [14080/27222 (52%)]      Loss: 0.540510
Train Epoch: 1 [14720/27222 (54%)]      Loss: 0.806726
Train Epoch: 1 [15360/27222 (56%)]      Loss: 0.486603
Train Epoch: 1 [16000/27222 (59%)]      Loss: 0.583694
Train Epoch: 1 [16640/27222 (61%)]      Loss: 0.504978
Train Epoch: 1 [17280/27222 (64%)]      Loss: 0.526972
Train Epoch: 1 [17920/27222 (66%)]      Loss: 0.569266
Train Epoch: 1 [18560/27222 (68%)]      Loss: 0.382459
Train Epoch: 1 [19200/27222 (71%)]      Loss: 0.590827
Train Epoch: 1 [19840/27222 (73%)]      Loss: 0.458023
Train Epoch: 1 [20480/27222 (75%)]      Loss: 0.375911
Train Epoch: 1 [21120/27222 (78%)]      Loss: 0.291837
Train Epoch: 1 [21760/27222 (80%)]      Loss: 0.536002
Train Epoch: 1 [22400/27222 (82%)]      Loss: 0.530014
Train Epoch: 1 [23040/27222 (85%)]      Loss: 0.606489
Train Epoch: 1 [23680/27222 (87%)]      Loss: 0.461238
Train Epoch: 1 [24320/27222 (89%)]      Loss: 0.333348
Train Epoch: 1 [24960/27222 (92%)]      Loss: 0.253399
Train Epoch: 1 [25600/27222 (94%)]      Loss: 0.353056
Train Epoch: 1 [26240/27222 (96%)]      Loss: 0.547270
Train Epoch: 1 [26880/27222 (99%)]      Loss: 0.483209

Test set: Average loss: 0.4349, Accuracy: 2572/3000 (85.7%)
```
Average training time per epoch:
```bash
30.63 seconds
```
