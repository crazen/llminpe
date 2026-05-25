import asyncio
import httpx
import time
import re

# Configurações do teste local
API_URL = "http://127.0.0.1:8000"
JWT_TOKEN = "PIBIC_EVAL_MASTER_SECRET_2026"  # Seu token mestre de bypass
SESSION_ID = "0701750d-d692-4dd9-91b4-16c520ac0783" 

# Uma única pergunta padrão bem completa para o benchmark
TEST_QUESTION = "O que é o sistema DETER e como ele funciona no monitoramento da Amazônia?"
GROUND_TRUTH = "O DETER é um sistema de alerta em tempo real desenvolvido pelo INPE para mapear e monitorar o desmatamento na Amazônia usando imagens orbitais."

CONFIGURATIONS = {
    "Baseline (FAISS)":    {"use_hyde": False, "use_multi_query": False, "use_reranking": False, "use_graph": False},
    "HyDE":                {"use_hyde": True,  "use_multi_query": False, "use_reranking": False, "use_graph": False},
    "Multi-Query":         {"use_hyde": False, "use_multi_query": True,  "use_reranking": False, "use_graph": False},
    "Reranking":           {"use_hyde": False, "use_multi_query": False, "use_reranking": True,  "use_graph": False},
    "Knowledge Graph":     {"use_hyde": False, "use_multi_query": False, "use_reranking": False, "use_graph": True},
    "HyDE + Reranking":    {"use_hyde": True,  "use_multi_query": False, "use_reranking": True,  "use_graph": False},
    "MQ + Reranking":      {"use_hyde": False, "use_multi_query": True,  "use_reranking": True,  "use_graph": False},
    "Todas as técnicas":   {"use_hyde": True,  "use_multi_query": True,  "use_reranking": True,  "use_graph": True}
}

def tokenize(text: str) -> set:
    return set(re.findall(r'\b\w{3,}\b', text.lower())) # Palavras com mais de 3 letras

async def test_endpoint(client: httpx.AsyncClient, name: str, toggles: dict):
    payload = {
        "session_id": SESSION_ID, "message": TEST_QUESTION,
        "use_hyde": toggles["use_hyde"], "use_multi_query": toggles["use_multi_query"],
        "use_reranking": toggles["use_reranking"], "use_graph": toggles["use_graph"]
    }
    headers = {"Authorization": f"Bearer {JWT_TOKEN}", "Content-Type": "application/json"}
    
    # Pausa de segurança entre requisições para a API respirar
    await asyncio.sleep(5.0)
    
    start_time = time.perf_counter()
    # Tenta primeiro a rota de stream, se der 404 tenta a rota normal
    for endpoint in ["/chat/stream", "/chat"]:
        try:
            response = await client.post(f"{API_URL}{endpoint}", json=payload, headers=headers, timeout=60.0)
            if response.status_code == 200:
                elapsed = time.perf_counter() - start_time
                
                # Coleta o texto da resposta (limpa marcações de Server-Sent Events se for stream)
                raw_text = response.text
                answer = "".join(re.findall(r'"answer":\s*"(.*?)"', raw_text)) or raw_text
                
                # Cálculo rápido de Overlap
                ans_tokens = tokenize(answer)
                gt_tokens = tokenize(GROUND_TRUTH)
                
                faith = len(ans_tokens.intersection(gt_tokens)) / len(ans_tokens) if ans_tokens else 0.5
                relev = len(tokenize(TEST_QUESTION).intersection(ans_tokens)) / len(tokenize(TEST_QUESTION)) if ans_tokens else 0.5
                
                print(f"  ✅ {name} processado com sucesso em {elapsed:.1f}s via {endpoint}")
                return {"Técnica": name, "Faithfulness": round(faith, 3), "Relevancy": round(relev, 3), "Tempo": round(elapsed, 1)}
        except Exception:
            pass
            
    print(f"  ❌ {name} falhou (Verifique se o backend está rodando na porta 8000)")
    return {"Técnica": name, "Faithfulness": 0.0, "Relevancy": 0.0, "Tempo": 0.0}

async def main():
    print("🚀 Iniciando Teste de Bancada Rápido (1 Pergunta por Técnica)...")
    results = []
    async with httpx.AsyncClient() as client:
        for name, toggles in CONFIGURATIONS.items():
            res = await test_endpoint(client, name, toggles)
            results.append(res)
            
    print("\n" + "="*65)
    print(f"{'TÉCNICA':<25} | {'FAITH.':<6} | {'RELEV.':<6} | {'TEMPO (s)'}")
    print("="*65)
    for r in results:
        print(f"{r['Técnica']:<25} | {r['Faithfulness']:<6} | {r['Relevancy']:<6} | {r['Tempo']}")
    print("="*65)

if __name__ == "__main__":
    asyncio.run(main())