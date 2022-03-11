from model_provider import ModelProvider, Sukima_ModelProvider, ModelGenRequest, ModelGenArgs, ModelSampleArgs, ModelLogitBiasArgs, ModelPhraseBiasArgs
import argparse
import json

def parse():
    parser = argparse.ArgumentParser(
        description="Sukima Research Tool is a tool for iterative-based testing on the Sukima API.",
        usage="srt [arguments]",
    )

    parser.add_argument(
        '-t', '--test',
        help="Path to the test file.",
        type=str,
        required=True
    )

    return parser.parse_args()

def config(args):
    with open(args.test) as f:
        return json.load(f)

def get_item(obj, key):
    if key in obj:
        return obj[key]
    else:
        return None

# update_item: if key is in obj and value is not None, update obj[key] to value
def update_item(obj, key, value):
    if value is not None:
        obj[key] = value

def get_model_provider(args):
    # load model provider gen_args into basemodel
    if 'model_provider' not in args:
        raise Exception('model_provider is not specified in config file.')
    if args["model_provider"]["name"] == "sukima":
        gen_args = ModelGenArgs(
            max_length=get_item(args["model_provider"]["gensettings"]["gen_args"], "max_length"),
            max_time=get_item(args["model_provider"]["gensettings"]["gen_args"], "max_time"),
            min_length=get_item(args["model_provider"]["gensettings"]["gen_args"], "min_length"),
            eos_token_id=get_item(args["model_provider"]["gensettings"]["gen_args"], "eos_token_id"),
            logprobs=get_item(args["model_provider"]["gensettings"]["gen_args"], "logprobs"),
            best_of=get_item(args["model_provider"]["gensettings"]["gen_args"], "best_of"),
        )
        # logit biases are an array in args['model_provider']['gensettings']['logit_biases']
        logit_biases = None
        if 'logit_biases' in args["model_provider"]["gensettings"]["sample_args"]:
            logit_biases = [ModelLogitBiasArgs(
                id=logit_bias["id"],
                bias=logit_bias["bias"]
            ) for logit_bias in args["model_provider"]["gensettings"]["sample_args"]["logit_biases"]]
        # phrase biases are an array in args['model_provider']['gensettings']['phrase_biases']
        phrase_biases = None
        if 'phrase_biases' in args["model_provider"]["gensettings"]["sample_args"]:
            phrase_biases = [ModelPhraseBiasArgs(
                sequences=phrase_bias["sequences"],
                bias=phrase_bias["bias"],
                ensure_sequence_finish=phrase_bias["ensure_sequence_finish"],
                generate_once=phrase_bias["generate_once"]
            ) for phrase_bias in args["model_provider"]["gensettings"]["sample_args"]["phrase_biases"]]
        
        sample_args = ModelSampleArgs(
            temp=get_item(args["model_provider"]["gensettings"]["sample_args"], "temp"),
            top_p=get_item(args["model_provider"]["gensettings"]["sample_args"], "top_p"),
            top_a=get_item(args["model_provider"]["gensettings"]["sample_args"], "top_a"),
            top_k=get_item(args["model_provider"]["gensettings"]["sample_args"], "top_k"),
            typical_p=get_item(args["model_provider"]["gensettings"]["sample_args"], "typical_p"),
            tfs=get_item(args["model_provider"]["gensettings"]["sample_args"], "tfs"),
            rep_p=get_item(args["model_provider"]["gensettings"]["sample_args"], "rep_p"),
            rep_p_range=get_item(args["model_provider"]["gensettings"]["sample_args"], "rep_p_range"),
            rep_p_slope=get_item(args["model_provider"]["gensettings"]["sample_args"], "rep_p_slope"),
            bad_words=get_item(args["model_provider"]["gensettings"]["sample_args"], "bad_words"),
            logit_biases=logit_biases,
            phrase_biases=phrase_biases
        )

        request = ModelGenRequest(
            model=args["model_provider"]["gensettings"]["model"],
            prompt=args["prompt"]+args["test_prompt"],
            sample_args=sample_args,
            gen_args=gen_args
        )

        return Sukima_ModelProvider(
            endpoint_url=args["model_provider"]["endpoint"],
            username=args["model_provider"]["username"],
            password=args["model_provider"]["password"],
            args=request
        )
    else:
        raise Exception('model_provider is not supported.')

def if_permutation(dict_loc, key):
    if key in dict_loc:
        return dict_loc[key]
    else:
        return None

import copy

def get_permutations(args, genreq: ModelGenRequest):
    if 'permutations' not in args:
        raise Exception('permutations is not specified in test file.')
    permutations = [] # array of ModelGenRequest to store permutations
    log_str = []

    if 'sample_args' in args['permutations']['gensettings']:
        temp = if_permutation(args['permutations']['gensettings']['sample_args'], 'temp')
        if temp is not None:
            for t in temp:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.temp = t
                permutations.append(permutation)
                log_str.append(f"temp: {t}")
        
        top_p = if_permutation(args['permutations']['gensettings']['sample_args'], 'top_p')
        if top_p is not None:
            for p in top_p:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.top_p = p
                permutations.append(permutation)
                log_str.append(f"top_p: {p}")
        
        top_a = if_permutation(args['permutations']['gensettings']['sample_args'], 'top_a')
        if top_a is not None:
            for a in top_a:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.top_a = a
                permutations.append(permutation)
                log_str.append(f"top_a: {a}")
        
        top_k = if_permutation(args['permutations']['gensettings']['sample_args'], 'top_k')
        if top_k is not None:
            for k in top_k:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.top_k = k
                permutations.append(permutation)
                log_str.append(f"top_k: {k}")
        
        typical_p = if_permutation(args['permutations']['gensettings']['sample_args'], 'typical_p')
        if typical_p is not None:
            for p in typical_p:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.typical_p = p
                permutations.append(permutation)
                log_str.append(f"typical_p: {p}")
        
        tfs = if_permutation(args['permutations']['gensettings']['sample_args'], 'tfs')
        if tfs is not None:
            for t in tfs:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.tfs = t
                permutations.append(permutation)
                log_str.append(f"tfs: {t}")
        
        rep_p = if_permutation(args['permutations']['gensettings']['sample_args'], 'rep_p')
        if rep_p is not None:
            for p in rep_p:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.rep_p = p
                permutations.append(permutation)
                log_str.append(f"rep_p: {p}")
        
        rep_p_range = if_permutation(args['permutations']['gensettings']['sample_args'], 'rep_p_range')
        if rep_p_range is not None:
            for r in rep_p_range:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.rep_p_range = r
                permutations.append(permutation)
                log_str.append(f"rep_p_range: {r}")
        
        rep_p_slope = if_permutation(args['permutations']['gensettings']['sample_args'], 'rep_p_slope')
        if rep_p_slope is not None:
            for s in rep_p_slope:
                permutation = copy.deepcopy(genreq)
                permutation.sample_args.rep_p_slope = s
                permutations.append(permutation)
                log_str.append(f"rep_p_slope: {s}")
    
    # gen_args
    if 'gen_args' in args['permutations']['gensettings']:
        max_length = if_permutation(args['permutations']['gensettings']['gen_args'], 'max_length')
        if max_length is not None:
            for l in max_length:
                permutation = copy.deepcopy(genreq)
                permutation.gen_args.max_length = l
                permutations.append(permutation)
                log_str.append(f"max_length: {l}")
        
        min_length = if_permutation(args['permutations']['gensettings']['gen_args'], 'min_length')
        if min_length is not None:
            for l in min_length:
                permutation = copy.deepcopy(genreq)
                permutation.gen_args.min_length = l
                permutations.append(permutation)
                log_str.append(f"min_length: {l}")
        
        eos_token_id = if_permutation(args['permutations']['gensettings']['gen_args'], 'eos_token_id')
        if eos_token_id is not None:
            for t in eos_token_id:
                permutation = copy.deepcopy(genreq)
                permutation.gen_args.eos_token_id = t
                permutations.append(permutation)
                log_str.append(f"eos_token_id: {t}")
        
        best_of = if_permutation(args['permutations']['gensettings']['gen_args'], 'best_of')
        if best_of is not None:
            for b in best_of:
                permutation = copy.deepcopy(genreq)
                permutation.gen_args.best_of = b
                permutations.append(permutation)
                log_str.append(f"best_of: {b}")
    
    return permutations, log_str