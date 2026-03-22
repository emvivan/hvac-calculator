 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..31d17b9510ecb1554eae908677ea5bb2c0d591e2
--- /dev/null
+++ b/README.md
@@ -0,0 +1,91 @@
+# Software HVAC - Cálculo de Carga Térmica
+
+Aplicação desktop em Python para cálculo de carga térmica HVAC com interface gráfica, biblioteca de materiais simples, elementos completos, vidros com SHGC e relatório PDF com gráfico de pizza em ReportLab.
+
+## Estrutura do projeto
+
+```text
+.
+├── main.py
+├── carga_termica.py
+├── gui/
+├── services/
+├── models/
+├── report/
+├── data/
+├── build_exe_windows.bat
+├── requirements.txt
+└── requirements-build.txt
+```
+
+## Funcionalidades implementadas
+
+- GUI desktop em Tkinter
+- seleção de cidade com auto preenchimento climático
+- biblioteca de materiais simples (`R = e / λ`)
+- biblioteca de elementos completos com U direto
+- montagem avançada de parede, cobertura e piso por camadas
+- vidro como elemento completo com U e SHGC
+- cálculo de cargas sensíveis e latentes
+- resultados em W, BTU/h, TR e percentuais
+- relatório PDF com tabelas e gráfico de pizza
+- base JSON pronta para expansão
+
+## Arquivos de dados
+
+- `data/materiais_simples.json`
+- `data/elementos_completos.json`
+- `data/vidros.json`
+- `data/cidades.json`
+
+## Como instalar
+
+```bash
+python -m pip install --upgrade pip
+python -m pip install -r requirements.txt
+```
+
+## Como executar
+
+```bash
+python main.py
+```
+
+ou:
+
+```bash
+python carga_termica.py
+```
+
+## Como usar
+
+1. Informe o nome do projeto.
+2. Escolha a cidade na lista.
+3. Revise os dados climáticos preenchidos automaticamente.
+4. Preencha o ambiente e as cargas internas.
+5. Na aba **Envoltória**, escolha o modo:
+   - **simples**: usa U direto de elementos completos
+   - **avançado**: monta camadas com materiais simples
+6. Cadastre o vidro com área, tipo, SHGC/SC e radiação.
+7. Clique em **Calcular**.
+8. Veja os resultados na aba **Resultados**.
+9. Clique em **Gerar PDF** para exportar o relatório.
+
+## Build do executável Windows
+
+```bat
+build_exe_windows.bat
+```
+
+Saída esperada:
+
+```text
+dist\HVACCargaTermica.exe
+```
+
+## Observações técnicas
+
+- Materiais simples não usam U direto; a resistência é calculada a partir da espessura e condutividade.
+- Vidros são sempre tratados como elementos completos.
+- O gráfico do PDF usa **ReportLab**, sem `matplotlib`.
+- A arquitetura foi organizada para expansão futura, inclusive para simulação horária.
 
EOF
)
