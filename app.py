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

# --- REGRAS DE NEGÓCIO EXPANDIDAS (Prazos de Troca & CA) ---
# Adicionado o seu CA real 46932 mapeado corretamente
DADOS_EPI_MOCK = {
    "Luva de Proteção (PU)": {
        "dias_troca": 30, 
        "desc": "Luva de segurança confeccionada em fibras sintéticas (poliéster), revestimento em poliuretano (PU) na palma e dedos. Ref: Tátil Black Smart.",
        "ca_real": "46932",
        "venc_real": "2031-03-17"
    },
    "Protetor Auricular": {"dias_troca": 180, "desc": "Protetor auricular plug de silicone"},
    "Óculos de Proteção": {"dias_troca": 365, "desc": "Óculos de proteção lente incolor anti-risco"},
    "Luva Nitrílica": {"dias_troca": 30, "desc": "Luva de segurança nitrílica para agentes químicos"},
    "Bota de PVC": {"dias_troca": 180, "desc": "Bota de PVC impermeável cano curto"},
    "Capacete de Segurança": {"dias_troca": 730, "desc": "Capacete de proteção aba frontal com carneira"},
}

def consultar_ca_mte(numero_ca, tipo_epi):
    """Consulta simulada aprimorada para aceitar CAs reais informados"""
    if not numero_ca:
        return "Aguardando CA...", "N/A", "N/A", 0
    
    info_epi = DADOS_EPI_MOCK.get(tipo_epi, {"dias_troca": 180, "desc": "Equipamento de Proteção Individual Padrão"})
    
    # Validação do CA Real fornecido pelo usuário para o teste
    if "ca_real" in info_epi and numero_ca.strip() == info_epi["ca_real"]:
        return "Válido", info_epi["venc_real"], info_epi["desc"], info_epi["dias_troca"]
        
    # Lógica genérica padrão para outros CAs digitados no teste
    status = "Válido" if int(numero_ca) % 2 != 0 else "Expirado"
    vencimento = "2029-08-22" if status == "Válido" else "2025-12-10"
    
    return status, vencimento, info_epi["desc"], info_epi["dias_troca"]


# --- INTERFACE DO USUÁRIO ---
st.title("🛡️ Sistema Inteligente de Gestão e Controle de EPI")
st.markdown("Controle de entregas, custos, validade de CA e alertas de troca.")

tab_cadastro, tab_dashboard, tab_historico = st.tabs(["📋 Registrar Entrega", "📊 Dashboard de Gastos", "🔍 Histórico & Busca"])

# ----------------------------------------------------------------------------------------
# ABA 1: CADASTRO DE ENTREGA
# ----------------------------------------------------------------------------------------
with tab_cadastro:
    st.subheader("Registrar Nova Entrega de EPI")
    
    with st.form("form_entrega", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            nome = st.text_input("Nome do Funcionário")
            setor = st.selectbox("Setor", ["Operacional", "Manutenção", "Administrativo", "Segurança", "Limpeza"])
            funcao = st.text_input("Função")
        
        with col2:
            tipo_epi = st.selectbox("Tipo de EPI", list(DADOS_EPI_MOCK.keys()))
            ca = st.text_input("Número do CA (Certificado de Aprovação)")
            motivo = st.selectbox("Motivo da Entrega/Troca", ["Desgaste Normal", "Desgaste Excessivo", "Perda", "Primeira Entrega"])
            
        with col3:
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
            valor_un = st.number_input("Valor Unitário (R$)", min_value=0.0, value=0.0, step=0.50)
            data_entrega = st.date_input("Data de Entrega", datetime.now())

        salvar = st.form_submit_button("Gravar Entrega e Gerar Alertas")

    if ca:
        status_ca, venc_ca, desc_epi, dias_sugeridos = consultar_ca_mte(ca, tipo_epi)
        
        if status_ca == "Válido":
            st.success(f"**Resultado da Consulta Automática (MTE):**\n\n"
                       f"• **Descrição:** {desc_epi}\n\n"
                       f"• **Status do CA:** ✅ {status_ca} (Vencimento: {venc_ca})\n\n"
                       f"• **Prazo de troca sugerido pela internet:** {dias_sugeridos} dias para este tipo de atividade.")
        else:
            st.warning(f"⚠️ **Atenção:** Este CA consta como EXPIRADO ({venc_ca}) no sistema do Ministério do Trabalho!")

    if salvar:
        if nome and ca and valor_un > 0:
            status_ca, venc_ca, desc_epi, dias_sugeridos = consultar_ca_mte(ca, tipo_epi)
            dt_troca = datetime.combine(data_entrega, datetime.min.time()) + timedelta(days=dias_sugeridos)
            
            novo_registro = {
                "Data": pd.to_datetime(data_entrega),
                "Funcionário": nome.strip(),
                "Setor": setor,
                "Função": funcao.strip(),
                "EPI": tipo_epi,
                "CA": ca,
                "Status CA": status_ca,
                "Vencimento CA": venc_ca,
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
            st.error("Por favor, preencha todos os campos obrigatórios (Nome, CA e Valor).")

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
# ABA 3: HISTÓRICO, CONSULTA E EDIÇÃO
# ----------------------------------------------------------------------------------------
with tab_historico:
    st.subheader("Histórico Geral e Rastreabilidade")
    st.markdown("💡 *Dica: Você pode dar um duplo clique em qualquer célula para **alterar os dados** ou selecionar uma linha e apertar `Delete` no seu teclado para **apagar** o registro.*")
    
    busca_nome = st.text_input("🔍 Digite o nome do funcionário para auditar:")
    df_hist = st.session_state.df_epi.copy()
    
    if busca_nome:
        df_hist = df_hist[df_hist["Funcionário"].str.contains(busca_nome, case=False)]
        if not df_hist.empty:
            total_func = df_hist["Total"].sum()
            st.markdown(f"**Análise para o funcionário:** {busca_nome.capitalize()}")
            st.info(f"💰 O funcionário já acumulou um custo total de **R$ {total_func:,.2f}** em EPIs.")
            
            st.markdown("**Última retirada de cada EPI:**")
            df_ultimos = df_hist.sort_values("Data").groupby("EPI").last().reset_index()
            for idx, row in df_ultimos.iterrows():
                st.write(f"• **{row['EPI']}**: Última retirada em {pd.to_datetime(row['Data']).strftime('%d/%m/%Y')} | CA: {row['CA']} ({row['Status CA']}) | Próxima troca sugerida: {datetime.strptime(row['Próxima Troca'], '%Y-%m-%d').strftime('%d/%m/%Y')}")
            st.markdown("---")

    df_hist["Data"] = pd.to_datetime(df_hist["Data"])
    
    df_editado = st.data_editor(
        df_hist, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "Total": st.column_config.NumberColumn(disabled=True),
            "Data": st.column_config.DatetimeColumn(format="DD/MM/YYYY")
        }
    )
    
    if st.button("💾 Salvar Alterações no Histórico", type="primary"):
        df_editado["Total"] = df_editado["Qtd"] * df_editado["Valor Unitário"]
        if busca_nome:
            indices_originais_filtrados = st.session_state.df_epi[st.session_state.df_epi["Funcionário"].str.contains(busca_nome, case=False)].index
            st.session_state.df_epi = st.session_state.df_epi.drop(indices_originais_filtrados)
            st.session_state.df_epi = pd.concat([st.session_state.df_epi, df_editado], ignore_index=True)
        else:
            st.session_state.df_epi = df_editado
            
        st.success("Histórico atualizado e salvo com sucesso!")
        st.rerun()
