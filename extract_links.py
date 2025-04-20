from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = Options()
# chrome_options.add_argument("--headless")  # opcional
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.agrolink.com.br/agrolinkfito/busca-simples-produto")

todos_links = set()
pagina = 1

try:
    while True:
        print(f"\n🔎 Página {pagina}...")

        # Aguarda os elementos da página serem carregados
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "block-result-main-title"))
        )

        # Encontra os elementos de título
        elementos = driver.find_elements(By.CLASS_NAME, "block-result-main-title")
        novos_links = 0
        for el in elementos:
            try:
                # Captura o atributo `href` logo após encontrar o elemento
                href = el.get_attribute("href")
                if href and href not in todos_links:
                    todos_links.add(href)
                    novos_links += 1
            except Exception as e:
                # Ignora elementos obsoletos
                print(f"⚠️ Erro ao acessar elemento: {e}")
                continue

        print(f"✅ {novos_links} novos links (Total: {len(todos_links)})")
        if len(todos_links) > 120:  # Condição de término
            break

        # Prepara a navegação
        pagina += 1
        script = f"navigateToPage('frmPesquisa', '{pagina}')"

        try:
            # Executa o script JavaScript para ir à próxima página
            driver.execute_script(script)
            time.sleep(2)  # Aguarde para garantir o carregamento da nova página
        except Exception as e:
            print(f"🚦 Última página ou erro ao chamar navigateToPage: {e}")
            break

finally:
    driver.quit()

# Salva todos os links em um arquivo
with open("todos_links.txt", "w", encoding="utf-8") as f:
    for link in sorted(todos_links):
        f.write(link + "\n")

print(f"\n🏁 Finalizado: {len(todos_links)} links salvos.")
