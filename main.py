import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from vllm import EngineArgs, LLMEngine, SamplingParams

import uuid


# LLM 엔진 초기 설정
engineargs = EngineArgs(
    model="models/",
    dtype='half',
    # tensor_parallel_size=2
    quantization='experts_int8',
    trust_remote_code=True,
    kv_cache_dtype='fp8',
    max_model_len=512,
    cpu_offload_gb=20,
    gpu_memory_utilization=0.8,

)
llm = LLMEngine.from_engine_args(engineargs)

sampling_params = SamplingParams(temperature=0.5, top_p=0.7, repetition_penalty=1.1, max_tokens=1024)


# 서버 설정
app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/generate")
async def generate_post(request: QueryRequest):
    
    request_id = str(uuid.uuid4())
    llm.add_request(request_id, request.query, sampling_params)
    sent_text = ""

    async def stream_response():
        nonlocal sent_text
        while True:
            request_outputs = llm.step()
            for output in request_outputs:
                if output.request_id == request_id:
                    text = output.outputs[0].text

                    # 새 텍스트만 추출 (기존에 출력한 텍스트는 응답하지 않도록)
                    new_text = text[len(sent_text):]
                    sent_text = text
                    
                    # 띄어쓰기 단위로 새로운 텍스트를 yield
                    for word in new_text.split(" "):
                        if word:  # 빈 문자열 제외
                            yield word + " "
                            # await asyncio.sleep(0.5)
                    
                    # 요청이 완료되면 종료
                    if output.finished:
                        return
                    
            await asyncio.sleep(0.1)

    return StreamingResponse(stream_response(), media_type="text/event-stream")