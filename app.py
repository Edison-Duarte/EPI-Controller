import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Gestão de EPI & Custos", layout="wide", page_icon="🛡️")

# --- SIMULAÇÃO DE BANCO DE DADOS (SESSION STATE) ---
if "df_epi" not in st.session_state:
    dados_iniciais = [
        {"Data": datetime(2026, 1, 15), "Funcionário": "João Silva", "Setor": "Operacional", "Função": "Marinheiro", "EPI": "Bota de PVC", "CA": "12345", "Status CA": "Válido", "Vencimento CA": "2028-12-31", "Qtd": 2, "Valor Unitário": 50.0, "Total": 100.0, "Motivo": "Desgaste Normal", "Próxima Troca": "2026-07-15"},
        {"Data": datetime(2026, 2, 10), "Funcionário": "Maria Souza", "Setor": "Manutenção", "Função": "Mecânico", "EPI": "Luva Nitrílica", "CA": "54321", "Status CA": "Válido", "Vencimento CA": "2027-05-18", "Qtd": 5, "Valor Unitário": 15.0, "Total": 75.0, "Motivo": "Desgaste Excessivo", "Próxima Troca": "2026-03-10"},
        {"Data": datetime(2026, 3, 5), "Funcionário": "Carlos Lima", "Setor": "Administrativo", "Função": "Vistoriador", "EPI": "Capacete de Segurança", "CA": "98765", "Status CA": "Válido", "Vencimento CA": "2029-01-01", "Qtd": 1, "Valor Unitário": 80.0, "Total": 80.0, "Motivo": "Perda", "Próxima Troca": "2027-03-05"},
    ]
    st.session_state.df_epi = pd.DataFrame(dados_iniciais)

# --- BANCO DE DADOS TEMPORÁRIO DOS CAS REAIS ---
BASE_CAS_REAIS = {
    "46932": {
        "EPI": "Luva de Proteção (PU)",
        "desc": "Luva de segurança confeccionada em fibras sintéticas (poliéster), 13 gauge, revestimento em poliuretano (PU) na palma e dedos. Ref: Tátil Black Smart.",
        "vencimento": "17/03/2031",
        "status": "VÁLIDO",
        "dias_troca": 30
    },
    "31895": {
        "EPI": "Luva de Proteção (Látex)",
        "desc": "Luva de segurança confeccionada em suporte têxtil com revestimento em látex natural corrugado na face palmar, dedos e dorso em 3/4. Fabricante: Super Safety.",
        "vencimento": "08/09/2027",
        "status": "VÁLIDO",
        "dias_troca": 45
    }
}

# --- INTERFACE DO USUÁRIO ---
st.title("🛡️ Sistema Inteligente de Gestão e Controle de EPI")
st.markdown("Controle de entregas, custos, validade de CA e alertas de troca.")

tab_cadastro, tab_dashboard, tab_historico = st.tabs(["📋 Registrar Entrega", "📊 Dashboard de Gastos", "🔍 Histórico & Busca"])

# ----------------------------------------------------------------------------------------
# ABA 1: CADASTRO DE ENTREGA
# ----------------------------------------------------------------------------------------
with tab_cadastro:
    st.subheader("Registrar Nova Entrega de EPI")
    
    col_ca1, col_ca2 = st.columns([3, 1])
    with col_ca1:
        ca_digitado = st.text_input("1. Digite o número do CA para buscar no MTE:", key="ca_input").strip()
    with col_ca2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("🌐 Consultar CA no MTE", "https://caepi.mte.gov.br/internet/ConsultaCAInternet.aspx", use_container_width=True)
    
    desc_automatica = ""
    venc_automatico = ""
    status_automatico = "Válido"
    dias_sugeridos = 30
    tipo_epi_sugerido = ""

    if ca_digitado:
        if ca_digitado in BASE_CAS_REAIS:
            dados_ca = BASE_CAS_REAIS[ca_digitado]
            desc_automatica = dados_ca["desc"]
            venc_automatico = dados_ca["vencimento"]
            status_automatico = dados_ca["status"]
            dias_sugeridos = dados_ca["dias_troca"]
            tipo_epi_sugerido = dados_ca["EPI"]
            
            st.success(f"**EPI Encontrado no MTE!**\n\n"
                       f"• **Equipamento:** {tipo_epi_sugerido}\n\n"
                       f"• **Descrição:** {desc_automatica}\n\n"
                       f"• **Situação:** ✅ {status_automatico} (Validade: {venc_automatico})\n\n"
                       f"• **Prazo de troca sugerido pela internet:** {dias_sugeridos} dias.")
        else:
            st.info("ℹ️ CA não pré-mapeado. Digite o tipo de EPI e setor livremente abaixo.")
            venc_automatico = "01/01/2030"
            desc_automatica = "Equipamento de Proteção Manual"

    st.markdown("---")
    st.markdown("**2. Dados Complementares da Entrega:**")
    
    with st.form("form_entrega", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            nome = st.text_input("Nome do Funcionário")
            setor = st.text_input("Setor")
            funcao = st.text_input("Função")
        
        with col2:
            tipo_epi = st.text_input("Tipo de EPI", value=tipo_epi_sugerido)
            motivo = st.selectbox("Motivo da Entrega/Troca", ["Desgaste Normal", "Desgaste Excessivo", "Perda", "Primeira Entrega"])
            data_entrega = st.date_input("Data de Entrega", datetime.now())
            
        with col3:
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
            valor_un = st.number_input("Valor Unitário (R$)", min_value=0.0, value=0.0, step=0.50)
            
        salvar = st.form_submit_button("Gravar Entrega no Histórico")

    if salvar:
        if nome and ca_digitado and valor_un > 0 and setor and tipo_epi:
            dt_troca = datetime.combine(data_entrega, datetime.min.time()) + timedelta(days=dias_sugeridos)
            
            novo_registro = {
                "Data": pd.to_datetime(data_entrega),
                "Funcionário": nome.strip(),
                "Setor": setor.strip(),
                "Função": funcao.strip(),
                "EPI": tipo_epi.strip(),
                "CA": ca_digitado,
                "Status CA": status_automatico,
                "Vencimento CA": venc_automatico,
                "Qtd": qtd,
                "Valor Unitário": valor_un,
                "Total": qtd * valor_un,
                "Motivo": motivo,
                "Próxima Troca": dt_troca.strftime('%Y-%m-%d')
            }
            
            st.session_state.df_epi = pd.concat([st.session_state.df_epi, pd.DataFrame([novo_registro])], ignore_index=True)
            st.success(f"EPI registrado com sucesso para {nome}! Próxima troca prevista para {dt_troca.strftime('%d/%m/%Y')}.")
            st.rerun()
        else:
            st.error("Por favor, preencha todos os campos obrigatórios (Nome, CA, Setor, Tipo de EPI e Valor Unitário).")

# ----------------------------------------------------------------------------------------
# ABA 2: DASHBOARD DE GASTOS
# ----------------------------------------------------------------------------------------
with tab_dashboard:
    st.subheader("Análise Estratégica de Custos")
    
    if not st.session_state.df_epi.empty:
        df_dash = st.session_state.df_epi.copy()
        df_dash["Data"] = pd.to_datetime(df_dash["Data"])
        
        st.sidebar.header("Filtros do Dashboard")
        min_date = df_dash["Data"].min().date()
        max_date = df_dash["Data"].max().date()
        periodo = st.sidebar.date_input("Período", [min_date, max_date])
        
        setores_disponiveis = df_dash["Setor"].unique().tolist()
        setores_selecionados = st.sidebar.multiselect("Setores", setores_disponiveis, default=setores_disponiveis)
        
        funcs_disponiveis = df_dash["Funcionário"].unique().tolist()
        funcs_selecionados = st.sidebar.multiselect("Funcionários", funcs_disponiveis, default=funcs_disponiveis)
        
        if len(periodo) == 2:
            df_dash = df_dash[(df_dash["Data"].dt.date >= periodo[0]) & (df_dash["Data"].dt.date <= periodo[1])]
        
        df_dash = df_dash[df_dash["Setor"].isin(setores_selecionados)]
        df_dash = df_dash[df_dash["Funcionário"].isin(funcs_selecionados)]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Gasto Total Filtrado", f"R$ {df_dash['Total'].sum():,.2f}")
        c2.metric("Total de Itens Entregues", int(df_dash['Qtd'].sum()))
        c3.metric("Trocas por Desgaste Excessivo/Perda", int(df_dash[df_dash["Motivo"].isin(["Desgaste Excessivo", "Perda"])].shape[0]))
        
        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Gasto Mensal de EPI**")
            df_dash["Ano-Mês"] = df_dash["Data"].dt.strftime("%Y-%m")
            gasto_mensal = df_dash.groupby("Ano-Mês")["Total"].sum().reset_index()
            fig_mensal = px.bar(gasto_mensal, x="Ano-Mês", y="Total", labels={"Total": "Custo (R$)"}, text_auto='.2s', color_discrete_sequence=["#00CC96"])
            st.plotly_chart(fig_mensal, use_container_width=True)
            
        with col_g2:
            st.markdown("**Gasto por Setor da Empresa**")
            gasto_setor = df_dash.groupby("Setor")["Total"].sum().reset_index()
            fig_setor = px.pie(gasto_setor, values="Total", names="Setor", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_setor, use_container_width=True)
            
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.markdown("**Motivos de Troca do EPI**")
            motivos_df = df_dash.groupby("Motivo")["Qtd"].sum().reset_index()
            fig_motivo = px.bar(motivos_df, x="Qtd", y="Motivo", orientation='h', color="Motivo", color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_motivo, use_container_width=True)
            
        with col_g4:
            st.markdown("**Top 5 Funcionários com Maior Custo**")
            top_func = df_dash.groupby("Funcionário")["Total"].sum().reset_index().sort_values(by="Total", ascending=False).head(5)
            fig_func = px.bar(top_func, x="Total", y="Funcionário", orientation='h', text_auto='.2s', color_discrete_sequence=["#636EFA"])
            st.plotly_chart(fig_func, use_container_width=True)
    else:
        st.info("Nenhum dado encontrado para os filtros selecionados.")

# ----------------------------------------------------------------------------------------
# ABA 3: HISTÓRICO, CONSULTA E EDIÇÃO (FILTROS DINÂMICOS BASEADOS NOS DADOS EXISTENTES)
# ----------------------------------------------------------------------------------------
with tab_historico:
    st.subheader("Histórico Geral e Rastreabilidade")
    st.markdown("💡 *Dica: Você pode filtrar antes de analisar ou alterar os dados diretamente na tabela abaixo.*")
    
    # Puxando dinamicamente as opções existentes no banco de dados para popular os filtros
    lista_setores = ["Todos"] + sorted(st.session_state.df_epi["Setor"].dropna().unique().tolist())
    lista_epis = ["Todos"] + sorted(st.session_state.df_epi["EPI"].dropna().unique().tolist())
    
    # Painel expansível contendo os filtros dinâmicos
    with st.expander("🔍 Painel de Filtros Avançados", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            busca_nome = st.text_input("Nome do Funcionário:")
            busca_setor = st.selectbox("Filtrar por Setor:", lista_setores) # Transformado em Menu Suspenso Inteligente
        with f_col2:
            busca_epi = st.selectbox("Filtrar por Tipo de EPI:", lista_epis) # Transformado em Menu Suspenso Inteligente
            busca_ca = st.text_input("Número do CA:")
        with f_col3:
            df_periodo = st.session_state.df_epi.copy()
            df_periodo["Data"] = pd.to_datetime(df_periodo["Data"])
            h_min_date = df_periodo["Data"].min().date() if not df_periodo.empty else datetime.now().date()
            h_max_date = df_periodo["Data"].max().date() if not df_periodo.empty else datetime.now().date()
            busca_periodo = st.date_input("Período de Entrega:", [h_min_date, h_max_date], key="busca_periodo_hist")

    # Copiando banco para aplicar filtros sucessivos
    df_filtrado_hist = st.session_state.df_epi.copy()
    df_filtrado_hist["Data"] = pd.to_datetime(df_filtrado_hist["Data"])
    
    # Aplicando os filtros na tabela
    if busca_nome:
        df_filtrado_hist = df_filtrado_hist[df_filtrado_hist["Funcionário"].str.contains(busca_nome, case=False)]
    if busca_setor != "Todos":
        df_filtrado_hist = df_filtrado_hist[df_filtrado_hist["Setor"] == busca_setor]
    if busca_epi != "Todos":
        df_filtrado_hist = df_filtrado_hist[df_filtrado_hist["EPI"] == busca_epi]
    if busca_ca:
        df_filtrado_hist = df_filtrado_hist[df_filtrado_hist["CA"].str.contains(busca_ca, case=False)]
    if len(busca_periodo) == 2:
        df_filtrado_hist = df_filtrado_hist[(df_filtrado_hist["Data"].dt.date >= busca_periodo[0]) & (df_filtrado_hist["Data"].dt.date <= busca_periodo[1])]

    # Exibindo métrica rápida do resultado filtrado
    if not df_filtrado_hist.empty:
        custo_filtrado_hist = df_filtrado_hist["Total"].sum()
        st.info(f"📊 Registros encontrados: **{df_filtrado_hist.shape[0]}** | Custo Acumulado do Filtro: **R$ {custo_filtrado_hist:,.2f}**")
    else:
        st.warning("⚠️ Nenhum registro encontrado para essa combinação de filtros.")

    # Renderizando o editor de dados com o dataframe filtrado
    df_editado = st.data_editor(
        df_filtrado_hist, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "Total": st.column_config.NumberColumn(disabled=True),
            "Data": st.column_config.DatetimeColumn(format="DD/MM/YYYY")
        }
    )
    
    if st.button("💾 Salvar Alterações no Histórico", type="primary"):
        df_editado["Total"] = df_editado["Qtd"] * df_editado["Valor Unitário"]
        
        # Se usou filtros, atualiza apenas as linhas que foram filtradas na tela
        if busca_nome or (busca_setor != "Todos") or (busca_epi != "Todos") or busca_ca or (len(busca_periodo) == 2):
            st.session_state.df_epi = st.session_state.df_epi.drop(df_filtrado_hist.index)
            st.session_state.df_epi = pd.concat([st.session_state.df_epi, df_editado], ignore_index=True)
        else:
            st.session_state.df_epi = df_editado
            
        st.success("Histórico atualizado com sucesso!")
        st.rerun()
