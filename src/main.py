import torch
import argparse

import pandas as pd


import utils
from hyperparameters_dev import HYPERPARAMETERS
from model_setup import CONFIGURATION


if __name__ == "__main__":

    device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Use GPU if available

    parser = argparse.ArgumentParser() # Argument Parser
    parser.add_argument('-t', '--train', help='Specify which languages to train on : es, fr, de, etc', nargs='+', type=str, required=True, action='store')
    parser.add_argument('-e', '--evaluate', help='Specify which languages to evaluate on : es, fr, de, etc', nargs='+', type=str, required=True, action='store')
    parser.add_argument('-m', '--model', help='Specify which model to use : cnn, bert, etc', nargs='+', type=str, required=True, action='store')

    args = parser.parse_args()

    df = pd.read_csv("../data/wiktionary_raw.csv")
    valid_args = utils.verify_args_are_valid(args, df)

    if valid_args:
        data = utils.clean_data(df)
        for model_ in args.model:
            config = CONFIGURATION[model_] 
            hyperparams = HYPERPARAMETERS[model_]
            train_loader, test_loader = utils.build_dataloaders(args, data, config)
            pretrained_model_path = utils.get_pretrained_file(args, model_)

            if pretrained_model_path.exists():
                clf = utils.load_pretrained_model(model_, hyperparams, pretrained_model_path)
            else:
                print(f"{model_} model will be trained on {args.train}")
                clf = utils.initialize_classifier(model_, hyperparams)
                clf.train_model(train_loader, device=device, num_epochs=5)
                torch.save(clf.state_dict(), pretrained_model_path)

            print(f"Testing {model_} model on {args.evaluate}")
            results = clf.evaluate(test_loader, device=device)
    else:
        print(f"Invalid arguments: please select from {utils.possible_options(df)}")