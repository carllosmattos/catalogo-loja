from pathlib import Path

Path("requirements.txt").write_text(
    "streamlit>=1.32\nsupabase==2.6.0\npython-dotenv\nPillow\nextra-streamlit-components>=0.1.71\n",
    encoding="utf-8",
)

Path("app.py").write_text(
    Path("app.py").read_text(encoding="utf-8")
    .replace(
        '    st.info("Verifique `.streamlit/secrets.toml` e as migrações em `supabase/migrations/`.")\n'
        '    st.page_link("pages/1_Admin_Login.py", label="Ir para o painel admin")',
        '    st.info("Tente novamente em alguns instantes.")',
    )
    .replace("inject_theme(settings)", "inject_theme(settings, hide_sidebar=True)")
    .replace(
        '    st.page_link("pages/1_Admin_Login.py", label="Acessar painel admin para cadastrar produtos")\n',
        "",
    )
    .replace(
        "\n# Menu acessível no mobile (seta >> no canto ou link abaixo)\n"
        'with st.expander("Menu"):\n'
        '    st.page_link("pages/1_Admin_Login.py", label="Painel admin")\n',
        "\n",
    ),
    encoding="utf-8",
)

print("patched")
