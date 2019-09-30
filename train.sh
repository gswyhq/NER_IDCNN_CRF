#!/bin/bash

export CUDA_VISIBLE_DEVICES=2,3

nohup python3 main.py --train=True --clean=True --model_type=bilstm --train_file=data/train3.txt --dev_file=data/dev3.txt --test_file=data/test3.txt > train_`date +%Y%m%d_%H%M%S`.log &




