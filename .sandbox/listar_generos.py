import csv
import os

def listar_generos():
    caminho_csv = 'detalhes_filmes.csv'
    
    if not os.path.exists(caminho_csv):
        print(f"Erro: Arquivo '{caminho_csv}' não encontrado.")
        return

    generos_unicos = set()
    total_filmes = 0
    filmes_sem_genero = 0

    with open(caminho_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_filmes += 1
            generos_raw = row.get('generos', '')
            
            if generos_raw and generos_raw.strip():
                # Supondo que os gêneros possam vir separados por vírgula no futuro
                lista = [g.strip() for g in generos_raw.split(',') if g.strip()]
                for g in lista:
                    generos_unicos.add(g)
            else:
                filmes_sem_genero += 1

    print(f"=== Análise de Gêneros ===")
    print(f"Total de filmes processados: {total_filmes}")
    print(f"Filmes sem gênero definido: {filmes_sem_genero}")
    print(f"Quantidade de gêneros únicos encontrados: {len(generos_unicos)}")
    print("\nLista de Gêneros:")
    for genero in sorted(list(generos_unicos)):
        print(f" - {genero}")

if __name__ == "__main__":
    listar_generos()
