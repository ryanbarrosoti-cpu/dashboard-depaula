import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestão De Paula", layout="wide")
st.title("💰 Controle Financeiro")

# Configurações da Planilha
SHEET_ID = "1fKCMVLg7b8Wn9fU02Rmmz75Vnz_umDecYj-cv9ceAXw"
GID = "1421929865" 
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=5)
def carregar_dados():
    df = pd.read_csv(url, dtype=str)
    
    def limpar_financeiro(v):
        if pd.isna(v) or str(v).strip() == "" or "nan" in str(v).lower():
            return 0.0
        # O SEGREDO: Remove R$, espaços normais e espaços invisíveis (\xa0)
        s = str(v).replace('R$', '').replace(' ', '').replace('\xa0', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(s)
        except:
            return 0.0

    # Mapeamento: D=3 (Valor), H=7 (Peças)
    df['N_Valor'] = df.iloc[:, 3].apply(limpar_financeiro)
    df['N_Pecas'] = df.iloc[:, 7].apply(limpar_financeiro)
    df['N_Lucro'] = df['N_Valor'] - df['N_Pecas']
    
    # Datas na Coluna C (2)
    df['Data_Ref'] = pd.to_datetime(df.iloc[:, 2], dayfirst=True, errors='coerce')
    df['Ano'] = df['Data_Ref'].dt.year.fillna(0).astype(int).astype(str)
    
    return df

def real(n):
    return f"R$ {n:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

try:
    df = carregar_dados()
    
    c1, c2, c3, c4 = st.columns(4)
    fat = df['N_Valor'].sum()
    lucro_total = df['N_Lucro'].sum()
    total_clientes = df.iloc[:, 1].dropna().count()
    
    status_vals = df.iloc[:, 9].astype(str).str.upper().str.strip()
    vencidos = len(df[status_vals == "VENCIDO"])

    with c1: st.metric("Faturamento Total", real(fat))
    with c2: st.metric("Lucro Líquido", real(lucro_total))
    with c3: st.metric("Clientes Atendidos", f"{total_clientes}")
    with c4: st.metric("Serviços Vencidos", vencidos)

    st.write("---")

    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("🏆 Ranking de Serviços")
        rank = df.iloc[:, 1].value_counts().reset_index()
        rank.columns = ['Serviço', 'Qtd']
        fig1 = px.bar(rank, x='Qtd', y='Serviço', orientation='h', text='Qtd', color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig1, use_container_width=True)

    with g2:
        st.subheader("📈 Lucro por Ano")
        df_ano = df[df['Ano'] != '0'].groupby('Ano')['N_Lucro'].sum().reset_index()
        if not df_ano.empty:
            fig2 = px.pie(df_ano, values='N_Lucro', names='Ano', hole=0.4)
            # AQUI: Troca porcentagem pelo valor em Dinheiro (R$)
            fig2.update_traces(
                textinfo='label+value',
                texttemplate='%{label}<br>R$ %{value:,.2f}'
            )
            fig2.update_layout(showlegend=False, separators=',.')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aguardando datas na Coluna C.")

except Exception as e:
    st.error(f"Erro: {e}")
