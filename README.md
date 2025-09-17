# Lukma TV – TV Corporativa (Streamlit + Google Sheets)

## Recursos
- Notícias com imagem responsiva (carrossel 10s)
- Previsão do tempo (4 unidades) com ticker rolando
- Aniversariantes do mês (animação + confete + GIF)
- Vídeos institucionais (playlist automática por duração)
- Relógios (Brasília, NY, Hong Kong)
- Cotações USD/EUR/BTC/ETH contra BRL
- Admin com login, permissões e CRUD (Google Sheets)

## Tecnologias
Streamlit, Google Sheets (gspread), streamlit-authenticator, Open-Meteo, exchangerate.host, CoinGecko.

## Como rodar
1. Configure Google Service Account e compartilhe a planilha “LukmaTV”.
2. Preencha `.env` (local) ou `.streamlit/secrets.toml` (deploy).
3. `pip install -r requirements.txt`
4. `streamlit run app_home.py`

## Estrutura de dados (Sheets)
- `news(id,title,description,image_url,active,order)`
- `videos(id,title,url,duration_seconds,active,order)`
- `birthdays(id,name,department,day,month,photo_url,active)`
- `users(username,full_name,role,password_hash,can_news,can_videos,can_birthdays,can_weather,can_fx,can_clocks)`
- `config(key,value)` → `weather_units` em JSON.

## Segurança
- Senhas **bcrypt** (não salve texto puro).
- Credenciais via `.env` / `secrets`.

## Padrões
- `black` p/ formatação (`black .`)
- `pytest` p/ testes (`pytest -q`)

## Deploy
- Use Streamlit Community Cloud (grátis). Informe `gcp_service_account` e `GOOGLE_SHEET_ID` em *Secrets*.

## Acessibilidade
- Imagens com legenda/descrição; contrastes fortes; sem JS custom perigoso.

## Próximos passos
- Cache agressivo para APIs públicas.
- Tela de “sala de espera” com QRCode e avisos.
- Logs/auditoria de alterações.
- Upload de imagens para um bucket (ex.: Cloudinary gratuito).
