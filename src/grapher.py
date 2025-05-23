import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from msg_debug import Debug as db

CLASSES = {0: '大', 1: '日', 2: '月', 3: '牛', 
           4: '翌', 5: '田', 6: '勿', 
           7: '矢', 8: '巳', 9: '木'}

def graph_training_acc(in_file, out_file):
    with open(in_file, "r") as file:
        data = np.genfromtxt(file, delimiter=',')
        
    k1 = [s[0] for s in data[:, 0].astype(str)]
    k2 = [s[1] for s in data[:, 0].astype(str)]
    dropout = [s[2:] for s in data[:, 0].astype(str)]
    ids = np.array([k1, k2, dropout])
    data = data[:, 1:]
    
    fig, axes = plt.subplots(3, 9, figsize=(27, 9), tight_layout=True)
    
    for i in range(data.shape[0]):
        row = i // 9
        col = i % 9
        print(f"{i}: {row}  {col}")
        
        axes[row, col].plot(data[i, :])
        axes[row, col].set_xlabel("Epochs")
        axes[row, col].set_ylabel("Testing Accuracy")
        axes[row, col].set_ylim(78, 100)
        axes[row, col].set_title(f"Accuracy for Model {ids[0, i]}_{ids[1, i]}_{ids[2, i]}")
        
    plt.subplots_adjust(right=2, bottom=2, top=4)
    
    plt.savefig(out_file, dpi=300)

def graph_class_acc(in_file, out_file):
    # https://stackoverflow.com/questions/21307832/how-to-display-chinese-in-matplotlib-plot
    # Using Microsoft YaHei (one of my faves)
    font = fm.FontProperties(fname='../data/msyh.ttc') 
    
    with open(in_file, "r") as file:
        data = np.genfromtxt(file, delimiter=',')
        
    k1 = [s[0] for s in data[:, 0].astype(str)]
    k2 = [s[1] for s in data[:, 0].astype(str)]
    dropout = [s[2:] for s in data[:, 0].astype(str)]
    ids = np.array([k1, k2, dropout])
    overall_acc = data[:, 1]
    data = data[:, 2:] * 100.
    
    labels = [f"Class {i} ({CLASSES[i]})" for i in range(0, 10)]
    
    fig, axes = plt.subplots(3, 9, figsize=(36, 12), tight_layout=True)
    
    for i in range(data.shape[0]):
        row = i // 9
        col = i % 9
        print(f"{i}: {row}  {col}")
        
        axes[row, col].bar(labels, data[i, :])
        axes[row, col].set_xlabel("Class")
        axes[row, col].set_ylabel("Accuracy")
        axes[row, col].set_xticklabels(labels, rotation=45, size='small', ha='right', rotation_mode='anchor', fontproperties=font)
        axes[row, col].set_ylim(0, 100)
        axes[row, col].set_title(f"Per-Class Accuracy for Model {ids[0, i]}_{ids[1, i]}_{ids[2, i]}")
        
    plt.subplots_adjust(right=8, bottom=8, top=10)
    
    plt.savefig(out_file, dpi=300)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', type=str)
    parser.add_argument('--out-file', type=str)
    # parser.add_argument('--read-file', type=str)
    parser.add_argument('--graph', type=str, choices=['training', 'classes'])
    args = parser.parse_args()
    
    if args.graph == 'training':
        graph_training_acc(args.in_file, args.out_file)
    elif args.graph == 'classes':
        graph_class_acc(args.in_file, args.out_file)
    
    
if __name__ == '__main__':
    main()