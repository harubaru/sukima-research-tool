import sys
import asyncio
import traceback
import os
import time

from args import parse, config, get_model_provider, get_permutations

def main():
    test = config(parse())
    model_provider = get_model_provider(test)
    permutations, log_strings = get_permutations(test, model_provider.kwargs['args'])

    os.makedirs(test['output_dir'], exist_ok=True)

    with open(f"{test['output_dir']}/{test['output']}", 'w', encoding='utf-8') as f:
        f.write(f"== Sukima API Research Tool ==\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}\nModel: {model_provider.kwargs['args'].model}\nSummary: {test['summary']}\n==============================\n\n")

    for i, permutation in enumerate(permutations):
        begin = time.time()
        completion = model_provider.generate(permutation)
        with open(f"{test['output_dir']}/{test['output']}", 'a', encoding='utf-8') as f:
            f.write(f"{log_strings[i]} -- {time.time()-begin:.2f} seconds\n{completion}\n")

if __name__ == '__main__':
    main()