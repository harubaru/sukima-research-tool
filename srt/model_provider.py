import aiohttp
from typing import Optional, List, Any
from pydantic import BaseModel
import requests
import json


class ModelGenArgs(BaseModel):
    max_length: int
    max_time: Optional[float] = None
    min_length: Optional[int] = None
    eos_token_id: Optional[int] = None
    logprobs: Optional[int] = None
    best_of: Optional[int] = None

    def toJSON(self):
        return json.dumps(self.dict())

class ModelLogitBiasArgs(BaseModel):
    id: int
    bias: float

    def toJSON(self):
        return json.dumps(self.dict())

class ModelPhraseBiasArgs(BaseModel):
    sequences: List[str]
    bias: float
    ensure_sequence_finish: bool
    generate_once: bool

    def toJSON(self):
        return json.dumps(self.dict())

class ModelSampleArgs(BaseModel):
    temp: Optional[float] = None
    top_p: Optional[float] = None
    top_a: Optional[float] = None
    top_k: Optional[int] = None
    typical_p: Optional[float] = None
    tfs: Optional[float] = None
    rep_p: Optional[float] = None
    rep_p_range: Optional[int] = None
    rep_p_slope: Optional[float] = None
    bad_words: Optional[List[str]] = None
    logit_biases: Optional[List[ModelLogitBiasArgs]] = None
    phrase_biases: Optional[List[ModelPhraseBiasArgs]] = None

    def toJSON(self):
        return json.dumps(self.dict())

class ModelGenRequest(BaseModel):
    model: str
    prompt: str
    softprompt: Optional[str] = None
    sample_args: ModelSampleArgs
    gen_args: ModelGenArgs

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        if __pydantic_self__.sample_args is None:
            __pydantic_self__.sample_args = ModelSampleArgs()
        if __pydantic_self__.gen_args is None:
            __pydantic_self__.gen_args = ModelGenArgs()

    def to_dict(self):
        return self.dict()
    
    def toJSON(self):
        return json.dumps(self.dict())

class ModelSerializer(json.JSONEncoder):
    """Class to serialize ModelGenRequest to JSON.
    """
    def default(self, o):
        if hasattr(o, 'toJSON'):
            return o.toJSON()
        return json.JSONEncoder.default(self, o)

class ModelProvider:
    """Abstract class for model providers that provide access to generative AI models.
    """
    def __init__(self, endpoint_url: str, **kwargs):
        """Constructor for ModelProvider.

        :param endpoint_url: The URL of the endpoint.
        :type endpoint_url: str
        """
        self.endpoint_url = endpoint_url
        self.kwargs = kwargs
        if 'args' not in kwargs:
            raise Exception('default args is required')
        self.auth()
    
    def auth(self):
        """Authenticate with the ModelProvider's endpoint.

        :raises NotImplementedError: If the authentication method is not implemented.
        """
        raise NotImplementedError('auth method is required')

    def generate(self, args):
        """Generate a response from the ModelProvider's endpoint.
        
        :param args: The arguments to pass to the endpoint.
        :type args: dict
        :raises NotImplementedError: If the generate method is not implemented.
        """
        raise NotImplementedError('generate method is required')

    def should_respond(self, context, name):
        """Determine if the ModelProvider predicts that the name should respond to the given context.

        :param context: The context to use.
        :type context: str
        :param name: The name to check.
        :type name: str
        :raises NotImplementedError: If the should_respond method is not implemented.
        """
        raise NotImplementedError('should_respond method is required')

    def response(self, context):
        """Generate a response from the ModelProvider's endpoint.
            
        :param context: The context to use.
        :type context: str
        :raises NotImplementedError: If the response method is not implemented.
        """
        raise NotImplementedError('response method is required')

class Sukima_ModelProvider(ModelProvider):
    def __init__(self, endpoint_url: str, **kwargs):
        """Constructor for Sukima_ModelProvider.

        :param endpoint_url: The URL for the Sukima endpoint.
        :type endpoint_url: str
        """

        super().__init__(endpoint_url, **kwargs)
        self.auth()
    
    def auth(self):
        """Authenticate with the Sukima endpoint.

        :raises Exception: If the authentication fails.
        """

        if 'username' not in self.kwargs and 'password' not in self.kwargs:
            raise Exception('username, password, and or token are not in kwargs')
        
        try:
            r = requests.post(f'{self.endpoint_url}/api/v1/users/token', data={'username': self.kwargs['username'], 'password': self.kwargs['password']}, timeout=10.0)
        except Exception as e:
            raise e
        if r.status_code == 200:
            self.token = r.json()['access_token']
        else:
            raise Exception(f'Could not authenticate with Sukima. Error: {r.text}')
        
    def generate(self, args: ModelGenRequest):
        """Generate a response from the Sukima endpoint.
        
        :param args: The arguments to pass to the endpoint.
        :type args: dict
        :return: The response from the endpoint.
        :rtype: str
        :raises Exception: If the request fails.
        """
        args = {
            'model': args.model,
            'prompt': args.prompt,
            'sample_args': {
                'temp': args.sample_args.temp,
                'top_p': args.sample_args.top_p,
                'top_a': args.sample_args.top_a,
                'top_k': args.sample_args.top_k,
                'typical_p': args.sample_args.typical_p,
                'tfs': args.sample_args.tfs,
                'rep_p': args.sample_args.rep_p,
                'rep_p_range': args.sample_args.rep_p_range,
                'rep_p_slope': args.sample_args.rep_p_slope,
                'bad_words': args.sample_args.bad_words
            },
            'gen_args': {
                'max_length': args.gen_args.max_length,
                'max_time': args.gen_args.max_time,
                'min_length': args.gen_args.min_length,
                'eos_token_id': args.gen_args.eos_token_id,
                'logprobs': args.gen_args.logprobs,
                'best_of': args.gen_args.best_of
            }
        }
        try:
            r = requests.post(f'{self.endpoint_url}/api/v1/models/generate', data=json.dumps(args), headers={'Authorization': f'Bearer {self.token}'}, timeout=120.0)
        except Exception as e:
            raise e
        if r.status_code == 200:
            return r.json()['output'][len(args['prompt']):]
        else:
            raise Exception(f'Could not generate text with Sukima. Error: {r.json()}')
    
    async def generate_async(self, args: ModelGenRequest):
        """Generate a response from the Sukima endpoint asynchronously.
        
        :param args: The arguments to pass to the endpoint.
        :type args: dict
        :return: The response from the endpoint.
        :rtype: str
        :raises Exception: If the request fails.
        """    
        args = {
            'model': args.model,
            'prompt': args.prompt,
            'sample_args': {
                'temp': args.sample_args.temp,
                'top_p': args.sample_args.top_p,
                'top_a': args.sample_args.top_a,
                'top_k': args.sample_args.top_k,
                'typical_p': args.sample_args.typical_p,
                'tfs': args.sample_args.tfs,
                'rep_p': args.sample_args.rep_p,
                'rep_p_range': args.sample_args.rep_p_range,
                'rep_p_slope': args.sample_args.rep_p_slope,
                'bad_words': args.sample_args.bad_words
            },
            'gen_args': {
                'max_length': args.gen_args.max_length,
                'max_time': args.gen_args.max_time,
                'min_length': args.gen_args.min_length,
                'eos_token_id': args.gen_args.eos_token_id,
                'logprobs': args.gen_args.logprobs,
                'best_of': args.gen_args.best_of
            }
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f'{self.endpoint_url}/api/v1/models/generate', json=args, headers={'Authorization': f'Bearer {self.token}'}, timeout=120.0) as resp:
                    if resp.status == 200:
                        js = await resp.json()
                        return js['output'][len(args['prompt']):]
                    else:
                        raise Exception(f'Could not generate response. Error: {resp.text}')
            except Exception as e:
                raise e

    def should_respond(self, context, name):
        """Determine if the Sukima endpoint predicts that the name should respond to the given context.

        :param context: The context to use.
        :type context: str
        :param name: The name to check.
        :type name: str
        :return: Whether or not the name should respond to the given context.
        :rtype: bool
        """
        phrase_bias = ModelPhraseBiasArgs
        phrase_bias.sequences = [name]
        phrase_bias.bias = 1.5
        phrase_bias.ensure_sequence_finish = True
        phrase_bias.generate_once = True

        args = self.kwargs['args'] # get default args
        args.prompt = context
        args.gen_args.eos_token_id = 25
        args.sample_args.temp = 0.25
        args.sample_args.phrase_biases = phrase_bias
        response = self.generate(args)
        if response.startswith(name):
            return True
        else:
            return False

    async def should_respond_async(self, context, name):
        """Determine if the Sukima endpoint predicts that the name should respond to the given context asynchronously.

        :param context: The context to use.
        :type context: str
        :param name: The name to check.
        :type name: str
        :return: Whether or not the name should respond to the given context.
        :rtype: bool
        """
        phrase_bias = ModelPhraseBiasArgs
        phrase_bias.sequences = [name]
        phrase_bias.bias = 1.5
        phrase_bias.ensure_sequence_finish = True
        phrase_bias.generate_once = True

        args = self.kwargs['args'] # get default args
        args.prompt = context
        args.gen_args.eos_token_id = 25
        args.sample_args.temp = 0.25
        args.sample_args.phrase_biases = phrase_bias
        response = await self.generate_async(args)
        if response.startswith(name):
            return True
        else:
            return False

    def response(self, context):
        """Generate a response from the Sukima endpoint.

        :param context: The context to use.
        :type context: str
        :return: The response from the endpoint.
        :rtype: str
        """
        args = self.kwargs['args']
        args.prompt = context
        args.gen_args.eos_token_id = 198
        args.gen_args.min_length = 1
        response = self.generate(args)
        return response

    async def response_async(self, context):
        """Generate a response from the Sukima endpoint asynchronously.

        :param context: The context to use.
        :type context: str
        :return: The response from the endpoint.
        :rtype: str
        """
        args = self.kwargs['args']
        args.prompt = context
        args.gen_args.eos_token_id = 198
        args.gen_args.min_length = 1
        response = await self.generate_async(args)
        return response

