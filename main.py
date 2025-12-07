import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Configuração básica e sessão
# ---------------------------------------------------------
st.set_page_config(
    page_title="Macaxeira – Custeio variável e preço",
    layout="wide"
)


def init_session_state():
    """Garante que as chaves que vamos usar existam na sessão."""
    default_keys = [
        "custo_variavel_unitario",
        "custo_variavel_total",
        "producao_final_kg",
        "area_ha",
        "produtividade_kg_ha",
        "perda_campo_percent",
        "perda_benef_percent",
    ]
    for k in default_keys:
        if k not in st.session_state:
            st.session_state[k] = None


# ---------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------
def slugify(text: str) -> str:
    """Gera uma chave simples para os widgets a partir de um texto."""
    return "".join(
        c.lower() if c.isalnum() else "_"
        for c in text
    )


def coletar_custos_etapa(etapa_id: str, titulo: str, itens: list) -> float:
    """
    Pergunta quantidade e custo unitário para cada item de uma etapa
    e devolve o custo total variável da etapa.
    """
    total = 0.0
    st.markdown(f"#### {titulo}")

    st.caption(
        "Preencha, para cada item, **quanto você usa** (quantidade) e **quanto paga por unidade** "
        "(custo unitário em R$). O sistema faz a conta do total automaticamente."
    )

    for i, item in enumerate(itens):
        item_id = f"{etapa_id}_{i}_{slugify(item['nome'])}"

        st.markdown(f"**{item['nome']}**")

        col1, col2, col3 = st.columns(3)
        with col1:
            qtd = st.number_input(
                f"Quantidade ({item.get('unidade_exemplo', 'unidade')})",
                min_value=0.0,
                step=1.0,
                key=f"{item_id}_qtd",
                help="Informe quanto desse item você usa no ciclo de produção considerado."
            )
        with col2:
            _ = st.text_input(
                "Unidade (ex: kg, saca, diária, hora)",
                value=item.get("unidade_exemplo", ""),
                key=f"{item_id}_unid"
            )
        with col3:
            custo_unit = st.number_input(
                "Custo unitário (R$)",
                min_value=0.0,
                step=0.01,
                key=f"{item_id}_custo_unit",
                help="Quanto custa **uma unidade** desse item (por kg, por diária, por hora, etc.)."
            )

        subtotal = qtd * custo_unit
        st.write(f"Custo deste item: **R$ {subtotal:,.2f}**")
        st.markdown("---")

        total += subtotal

    outros = st.number_input(
        f"Outros custos variáveis de {titulo.lower()} (total, em R$)",
        min_value=0.0,
        step=10.0,
        key=f"{etapa_id}_outros",
        help="Use este campo se tiver algum gasto variável que não entrou nos itens acima."
    )
    total += outros

    st.write(f"**Total de custos variáveis de {titulo}: R$ {total:,.2f}**")
    st.markdown("---")
    return total


# ---------------------------------------------------------
# Página 1 – Custeio variável
# ---------------------------------------------------------
def pagina_custeio_variavel():
    st.header("1. Custeio variável da macaxeira – do plantio à venda")

    with st.expander("O que esta aba faz? (clique para ver)", expanded=True):
        st.write(
            "Nesta parte, o sistema soma **todos os gastos que aumentam quando você produz mais** "
            "macaxeira (sementes, adubos, diárias, embalagens, energia, frete etc.).\n\n"
            "No final, ele mostra **quanto custa, em média, produzir 1 kg de macaxeira pronta para vender**. "
            "Esse é o **custo variável por kg**, que será usado depois para simulação e formação do preço de venda."
        )

    st.subheader("Dados de produção do ciclo")
    st.caption(
        "Aqui você informa **quanto está produzindo** e **quanto perde** no caminho "
        "(no campo e no beneficiamento). O sistema usa isso para calcular quantos kg realmente chegam para venda."
    )

    col1, col2 = st.columns(2)
    with col1:
        area_ha = st.number_input(
            "Área plantada (ha)",
            min_value=0.0,
            step=0.1,
            value=st.session_state["area_ha"] or 1.0,
            key="area_ha_input",
            help="Informe quantos hectares de macaxeira foram plantados."
        )
    with col2:
        produtividade_kg_ha = st.number_input(
            "Produtividade esperada de raiz colhida (kg/ha)",
            min_value=0.0,
            step=100.0,
            value=st.session_state["produtividade_kg_ha"] or 20000.0,
            key="produtividade_kg_ha_input",
            help="Quantos kg de raiz você espera colher, em média, por hectare."
        )

    col3, col4 = st.columns(2)
    with col3:
        perda_campo_percent = st.number_input(
            "Perdas na lavoura / colheita (% sobre a raiz colhida)",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            value=st.session_state["perda_campo_percent"] or 5.0,
            key="perda_campo_input",
            help="Percentual que se perde no campo (raízes danificadas, que ficam no solo, etc.)."
        )
    with col4:
        perda_benef_percent = st.number_input(
            "Perdas no beneficiamento e pós-colheita (% sobre o que sai da lavoura)",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            value=st.session_state["perda_benef_percent"] or 20.0,
            key="perda_benef_input",
            help="Percentual que se perde no descasque, cortes, lavagens, aparas, etc."
        )

    st.markdown("---")

    st.subheader("Custos variáveis por etapa")
    st.caption(
        "Preencha, em cada etapa, os **gastos que aumentam quando você produz mais**. "
        "Gastos fixos (como aluguel, um salário fixo mensal) não entram aqui."
    )

    with st.expander("Etapa 1 – Plantio", expanded=False):
        st.write(
            "Inclua aqui os gastos ligados ao **início da lavoura**: limpeza, preparo do solo, "
            "mudas, adubação de fundação e mão de obra dessa fase."
        )
        itens_plantio = [
            {
                "nome": "Mudas / manivas para plantio",
                "unidade_exemplo": "mil mudas",
            },
            {
                "nome": "Adubação de fundação (fertilizantes, corretivos etc.)",
                "unidade_exemplo": "kg ou sacas",
            },
            {
                "nome": "Mão de obra (limpeza, preparo do solo, marcação das linhas, plantio)",
                "unidade_exemplo": "diárias",
            },
            {
                "nome": "Máquinas / equipamentos (roçadeira, trator, implementos) – uso no plantio",
                "unidade_exemplo": "horas",
            },
        ]
        custo_plantio = coletar_custos_etapa("plantio", "Plantio", itens_plantio)

    with st.expander("Etapa 2 – Condução da cultura", expanded=False):
        st.write(
            "Aqui entram os gastos para **cuidar da lavoura até a colheita**: adubação de cobertura, "
            "cultivo do solo, trituração e manejo em geral."
        )
        itens_conducao = [
            {
                "nome": "Adubação de cobertura 1",
                "unidade_exemplo": "kg ou sacas",
            },
            {
                "nome": "Adubação de cobertura 2",
                "unidade_exemplo": "kg ou sacas",
            },
            {
                "nome": "Mão de obra (cultivo do solo, trituração de resíduos, manejo geral)",
                "unidade_exemplo": "diárias",
            },
            {
                "nome": "Máquinas / equipamentos (trituração, cultivo, trator etc.)",
                "unidade_exemplo": "horas",
            },
            {
                "nome": "Defensivos / outros insumos de manejo",
                "unidade_exemplo": "unidades",
            },
        ]
        custo_conducao = coletar_custos_etapa("conducao", "Condução da cultura", itens_conducao)

    with st.expander("Etapa 3 – Colheita e pós-colheita (da lavoura até a expedição)", expanded=False):
        st.write(
            "Aqui entram os gastos para **colher, beneficiar e entregar** a macaxeira: "
            "mão de obra, embalagens, água, produtos de limpeza, energia, frete etc."
        )
        itens_pos = [
            {
                "nome": "Mão de obra de colheita",
                "unidade_exemplo": "diárias",
            },
            {
                "nome": "Mão de obra de beneficiamento (pesagem, descasque, lavagens, drenagem, embalagem, rotulagem)",
                "unidade_exemplo": "diárias",
            },
            {
                "nome": "Embalagens (sacos, bandejas, filmes, caixas)",
                "unidade_exemplo": "unidades",
            },
            {
                "nome": "Rótulos / etiquetas",
                "unidade_exemplo": "unidades",
            },
            {
                "nome": "Água, produtos de limpeza, cloro etc.",
                "unidade_exemplo": "litros ou unidades",
            },
            {
                "nome": "Energia elétrica variável ligada ao processamento",
                "unidade_exemplo": "kWh (ou informe total em R$ com quantidade = 1)",
            },
            {
                "nome": "Frete / transporte até o cliente ou ponto de venda (informe total da safra, se quiser)",
                "unidade_exemplo": "viagens (ou quantidade = 1 para total)",
            },
        ]
        custo_pos = coletar_custos_etapa("pos_colheita", "Colheita e pós-colheita", itens_pos)

    custo_total_variavel = custo_plantio + custo_conducao + custo_pos

    # Cálculos de produção
    producao_raiz_kg = area_ha * produtividade_kg_ha
    producao_pos_campo_kg = producao_raiz_kg * (1 - perda_campo_percent / 100.0)
    producao_final_kg = producao_pos_campo_kg * (1 - perda_benef_percent / 100.0)

    st.markdown("### Resultados do custeio variável")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(
            "Produção de raiz colhida (kg)",
            f"{producao_raiz_kg:,.2f}"
        )
    with col_res2:
        st.metric(
            "Produção final vendável (kg)",
            f"{producao_final_kg:,.2f}"
        )
    with col_res3:
        st.metric(
            "Custo variável total (R$)",
            f"{custo_total_variavel:,.2f}"
        )

    if producao_final_kg > 0:
        custo_variavel_unitario = custo_total_variavel / producao_final_kg
        st.success(
            f"Custo variável unitário aproximado: **R$ {custo_variavel_unitario:,.4f} por kg de macaxeira vendável**"
        )
        st.caption(
            "Isso significa: em média, **produzir 1 kg pronto para venda custa esse valor em gastos que variam com a produção**. "
            "Esse número será a base para a simulação de cenários e para calcular o preço de venda."
        )

        # Guarda na sessão para usar nas outras páginas
        st.session_state["custo_variavel_unitario"] = custo_variavel_unitario
        st.session_state["custo_variavel_total"] = custo_total_variavel
        st.session_state["producao_final_kg"] = producao_final_kg
        st.session_state["area_ha"] = area_ha
        st.session_state["produtividade_kg_ha"] = produtividade_kg_ha
        st.session_state["perda_campo_percent"] = perda_campo_percent
        st.session_state["perda_benef_percent"] = perda_benef_percent
    else:
        st.error("A produção final vendável ficou igual a zero. Ajuste os dados de produção e perdas.")


# ---------------------------------------------------------
# Página 2 – Simulação Monte Carlo
# ---------------------------------------------------------
def pagina_monte_carlo():
    st.header("2. Simulação de cenários (Monte Carlo)")

    with st.expander("O que esta aba faz? (clique para ver)", expanded=True):
        st.write(
            "Aqui o sistema faz **vários cenários possíveis** para a sua produção, mudando três coisas:\n"
            "- produtividade (kg/ha),\n"
            "- preço de venda (R$/kg),\n"
            "- custo variável por kg.\n\n"
            "Em cada cenário ele calcula **quanto sobraria (margem) para pagar custos fixos e lucro**. "
            "Assim você enxerga o **risco de prejuízo** e a faixa provável de resultado."
        )

    st.write(
        "Preencha abaixo os valores **mínimo, mais provável e máximo** para produtividade, preço e custo variável. "
        "Com isso o app cria muitos cenários aleatórios entre esses valores."
    )

    col1, col2 = st.columns(2)
    with col1:
        n_sim = st.number_input(
            "Número de simulações (quantidade de cenários gerados)",
            min_value=1000,
            max_value=50000,
            step=1000,
            value=10000,
            help="Quanto maior o número, mais Cenários o sistema cria. 10.000 já costuma ser um bom valor."
        )
    with col2:
        area_ha_sim = st.number_input(
            "Área considerada na simulação (ha)",
            min_value=0.0,
            step=0.1,
            value=st.session_state["area_ha"] or 1.0,
            help="Quantos hectares de macaxeira você quer considerar nesses cenários."
        )

    st.markdown("#### Produtividade (kg/ha) – distribuição triangular")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        prod_min = st.number_input(
            "Produtividade mínima (kg/ha)",
            min_value=0.0,
            step=100.0,
            value=15000.0,
            help="Cenário ruim: quantos kg/ha se a safra for fraca."
        )
    with col_p2:
        prod_most = st.number_input(
            "Produtividade mais provável (kg/ha)",
            min_value=0.0,
            step=100.0,
            value=st.session_state["produtividade_kg_ha"] or 20000.0,
            help="Valor que você acha mais realista para a produtividade."
        )
    with col_p3:
        prod_max = st.number_input(
            "Produtividade máxima (kg/ha)",
            min_value=0.0,
            step=100.0,
            value=25000.0,
            help="Cenário muito bom: quantos kg/ha se tudo der certo."
        )

    st.markdown("#### Preço de venda da macaxeira (R$/kg) – distribuição triangular")
    col_pre1, col_pre2, col_pre3 = st.columns(3)
    with col_pre1:
        preco_min = st.number_input(
            "Preço mínimo (R$/kg)",
            min_value=0.0,
            step=0.10,
            value=2.00,
            help="Preço em um cenário ruim de mercado."
        )
    with col_pre2:
        preco_most = st.number_input(
            "Preço mais provável (R$/kg)",
            min_value=0.0,
            step=0.10,
            value=2.50,
            help="Preço que você acredita ser o mais comum."
        )
    with col_pre3:
        preco_max = st.number_input(
            "Preço máximo (R$/kg)",
            min_value=0.0,
            step=0.10,
            value=3.00,
            help="Preço em um cenário muito favorável."
        )

    st.markdown("#### Custo variável unitário (R$/kg) – distribuição triangular")
    cvu_base = st.session_state["custo_variavel_unitario"] or 1.50

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cvu_min = st.number_input(
            "Custo variável mínimo (R$/kg)",
            min_value=0.0,
            step=0.05,
            value=float(max(cvu_base * 0.8, 0.0)),
            help="Cenário em que os gastos variáveis saem mais baratos."
        )
    with col_c2:
        cvu_most = st.number_input(
            "Custo variável mais provável (R$/kg)",
            min_value=0.0,
            step=0.05,
            value=float(cvu_base),
            help="Custo variável por kg que você considera mais provável."
        )
    with col_c3:
        cvu_max = st.number_input(
            "Custo variável máximo (R$/kg)",
            min_value=0.0,
            step=0.05,
            value=float(cvu_base * 1.2),
            help="Cenário em que o custo variável fica mais caro que o normal."
        )

    if st.button("Rodar simulação"):
        # Checagens simples
        if not (prod_min <= prod_most <= prod_max):
            st.error("Produtividade: garanta que mínimo ≤ mais provável ≤ máximo.")
            return
        if not (preco_min <= preco_most <= preco_max):
            st.error("Preço: garanta que mínimo ≤ mais provável ≤ máximo.")
            return
        if not (cvu_min <= cvu_most <= cvu_max):
            st.error("Custo variável: garanta que mínimo ≤ mais provável ≤ máximo.")
            return

        # Geração das amostras
        prod_samples = np.random.triangular(prod_min, prod_most, prod_max, int(n_sim))
        preco_samples = np.random.triangular(preco_min, preco_most, preco_max, int(n_sim))
        cvu_samples = np.random.triangular(cvu_min, cvu_most, cvu_max, int(n_sim))

        producao_total = prod_samples * area_ha_sim
        receita_total = preco_samples * producao_total
        custo_variavel_total = cvu_samples * producao_total
        margem_total = receita_total - custo_variavel_total
        margem_unitaria = preco_samples - cvu_samples

        df = pd.DataFrame({
            "Produtividade_kg_ha": prod_samples,
            "Preço_R$/kg": preco_samples,
            "Custo_var_R$/kg": cvu_samples,
            "Produção_total_kg": producao_total,
            "Receita_total_R$": receita_total,
            "Custo_var_total_R$": custo_variavel_total,
            "Margem_total_R$": margem_total,
            "Margem_unit_R$/kg": margem_unitaria,
        })

        margem_total_media = df["Margem_total_R$"].mean()
        prob_prejuizo = (df["Margem_total_R$"] < 0).mean() * 100
        margem_unit_media = df["Margem_unit_R$/kg"].mean()

        st.markdown("### Resultados resumidos da simulação")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric(
                "Margem total média (R$)",
                f"{margem_total_media:,.2f}"
            )
        with col_r2:
            st.metric(
                "Probabilidade de margem total negativa",
                f"{prob_prejuizo:,.1f} %"
            )
        with col_r3:
            st.metric(
                "Margem unitária média (R$/kg)",
                f"{margem_unit_media:,.4f}"
            )

        st.caption(
            f"Em linguagem simples: em média, a atividade deixaria cerca de **R$ {margem_total_media:,.2f}** "
            f"para pagar custos fixos e lucro. Em aproximadamente **{prob_prejuizo:,.1f}%** dos cenários, "
            "a margem fica negativa (ou seja, **não sobra nada para fixos e lucro**)."
        )

        st.markdown("#### Estatísticas principais (valores simulados)")
        st.dataframe(
            df[["Receita_total_R$", "Custo_var_total_R$", "Margem_total_R$", "Margem_unit_R$/kg"]]
            .describe()
            .T
        )

        st.markdown("#### Distribuição da margem total (R$)")
        fig, ax = plt.subplots()
        ax.hist(df["Margem_total_R$"], bins=30)
        ax.set_xlabel("Margem total (R$)")
        ax.set_ylabel("Quantidade de cenários")
        st.pyplot(fig)

        st.caption(
            "O gráfico mostra **quantos cenários** ficaram em cada faixa de resultado. "
            "Valores mais à direita significam margens maiores; valores à esquerda, margens menores ou negativas."
        )


# ---------------------------------------------------------
# Página 3 – Precificação com markup
# ---------------------------------------------------------
def pagina_precificacao():
    st.header("3. Precificação com base em custeio variável e markup")

    with st.expander("O que esta aba faz? (clique para ver)", expanded=True):
        st.write(
            "Aqui o objetivo é **chegar em um preço de venda por kg** que:\n"
            "- pague o **custo variável por kg**;\n"
            "- ajude a pagar os **custos fixos** que você quer cobrir com essa produção;\n"
            "- gere o **lucro desejado**;\n"
            "- considere **impostos** e outras despesas sobre o faturamento.\n\n"
            "O cálculo usa a ideia de **markup**: o preço é um múltiplo do custo variável, "
            "ajustado para cobrir tudo isso."
        )

    # Custo variável unitário
    st.subheader("Custo variável unitário")
    st.caption(
        "Se você já fez o custeio na primeira aba, pode reaproveitar o valor calculado lá. "
        "Se preferir, pode informar um valor manualmente."
    )

    usa_cvu_calculado = False
    if st.session_state["custo_variavel_unitario"] is not None:
        usa_cvu_calculado = st.checkbox(
            "Usar o custo variável unitário calculado na aba de Custeio variável",
            value=True
        )

    if usa_cvu_calculado:
        cvu = st.session_state["custo_variavel_unitario"]
        st.info(f"Custo variável unitário considerado: **R$ {cvu:,.4f} por kg**.")
    else:
        cvu = st.number_input(
            "Informe o custo variável unitário (R$/kg)",
            min_value=0.0,
            step=0.01,
            value=1.50,
            help="Se não usou a primeira aba, informe aqui o custo variável médio por kg."
        )

    st.markdown("---")

    st.subheader("Custos fixos e lucro desejado para esta produção")
    st.caption(
        "Aqui você diz **quanto de custo fixo** quer cobrir com esta produção "
        "(ex.: parte do salário fixo, energia mínima, aluguel etc.) e "
        "**quanto de lucro** deseja obter."
    )

    col_cf1, col_cf2 = st.columns(2)
    with col_cf1:
        custos_fixos_totais = st.number_input(
            "Total de custos fixos que deseja cobrir com esta produção (R$)",
            min_value=0.0,
            step=100.0,
            value=0.0,
            help="Some os custos fixos que você deseja que esta produção ajude a pagar."
        )
    with col_cf2:
        lucro_desejado_total = st.number_input(
            "Lucro total desejado com esta produção (R$)",
            min_value=0.0,
            step=100.0,
            value=0.0,
            help="Quanto você gostaria de ganhar de lucro com essa produção."
        )

    volume_padrao = st.session_state["producao_final_kg"] or 0.0
    volume_previsto_kg = st.number_input(
        "Volume previsto de venda desta produção (kg)",
        min_value=0.0,
        step=10.0,
        value=float(volume_padrao),
        help="Quantos kg de macaxeira você espera vender dessa produção."
    )

    st.markdown("---")

    st.subheader("Percentuais sobre o faturamento (despesas variáveis e impostos)")
    st.caption(
        "Informe, em percentual, **quanto do preço de venda** é consumido por impostos "
        "e despesas variáveis comerciais (frete, comissão, taxas de cartão etc.)."
    )

    col_tx1, col_tx2 = st.columns(2)
    with col_tx1:
        impostos_percent = st.number_input(
            "Impostos sobre faturamento (% do preço de venda)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            value=0.0,
            help="Percentual de impostos cobrados sobre o faturamento (ex.: 5%, 10%)."
        )
    with col_tx2:
        desp_var_percent = st.number_input(
            "Despesas variáveis comerciais (frete, comissões etc.) (% do preço)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            value=0.0,
            help="Percentual de gastos ligados à venda (fretes que variam, comissões, taxas, etc.)."
        )

    if st.button("Calcular preço com markup"):
        if cvu <= 0:
            st.error("Informe um custo variável unitário maior que zero.")
            return
        if volume_previsto_kg <= 0:
            st.error("Informe um volume previsto de venda maior que zero.")
            return

        t_imp = impostos_percent / 100.0
        t_dv = desp_var_percent / 100.0
        soma_tx = t_imp + t_dv
        if soma_tx >= 1:
            st.error("A soma de impostos + despesas variáveis deve ser menor que 100%.")
            return

        # Margem de contribuição unitária desejada para cobrir fixos + lucro
        mc_unit_desejada = (custos_fixos_totais + lucro_desejado_total) / volume_previsto_kg

        # Fórmula:
        # P * (1 - t_imp - t_dv) - CVU = MC_unit_desejada
        # P = (CVU + MC_unit_desejada) / (1 - t_imp - t_dv)
        denom = 1 - soma_tx
        preco_sugerido = (cvu + mc_unit_desejada) / denom

        custo_fixo_unit = custos_fixos_totais / volume_previsto_kg if volume_previsto_kg > 0 else 0.0
        lucro_unit_desejado = lucro_desejado_total / volume_previsto_kg if volume_previsto_kg > 0 else 0.0

        impostos_unit = preco_sugerido * t_imp
        desp_var_unit = preco_sugerido * t_dv

        mc_unit_real = preco_sugerido - cvu - impostos_unit - desp_var_unit
        mc_total_real = mc_unit_real * volume_previsto_kg
        lucro_total_real = mc_total_real - custos_fixos_totais

        markup_efetivo = preco_sugerido / cvu

        st.markdown("### Resultado da formação de preço com markup")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric(
                "Preço de venda sugerido (R$/kg)",
                f"{preco_sugerido:,.4f}"
            )
        with col_r2:
            st.metric(
                "Markup efetivo sobre o custo variável",
                f"{markup_efetivo:,.2f} x"
            )
        with col_r3:
            st.metric(
                "Margem de contribuição unitária obtida (R$/kg)",
                f"{mc_unit_real:,.4f}"
            )

        st.caption(
            f"Isso significa que, para cada kg vendido a esse preço, **sobra cerca de R$ {mc_unit_real:,.4f}** "
            "de margem para pagar os custos fixos e gerar lucro."
        )

        st.markdown("#### Decomposição unitária do preço (por kg)")
        st.write(f"- Custo variável unitário: **R$ {cvu:,.4f}**")
        st.write(f"- Impostos: **R$ {impostos_unit:,.4f}**")
        st.write(f"- Despesas variáveis comerciais: **R$ {desp_var_unit:,.4f}**")
        st.write(f"- Custo fixo unitário (meta): **R$ {custo_fixo_unit:,.4f}**")
        st.write(f"- Lucro unitário desejado (meta): **R$ {lucro_unit_desejado:,.4f}**")

        st.markdown("#### Resultado global estimado para a produção")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.metric(
                "Margem de contribuição total (R$)",
                f"{mc_total_real:,.2f}"
            )
        with col_g2:
            st.metric(
                "Lucro total estimado (R$)",
                f"{lucro_total_real:,.2f}"
            )

        if lucro_total_real >= lucro_desejado_total - 1:
            st.success(
                "Com esse preço, a meta de pagar os custos fixos e atingir o lucro desejado está "
                "atingida (ou muito próxima, considerando arredondamentos)."
            )
        else:
            st.warning(
                "Com esse preço, o lucro estimado ficou abaixo do lucro desejado. "
                "Você pode ajustar o lucro desejado, o volume previsto ou rever as porcentagens "
                "de impostos e despesas variáveis."
            )


# ---------------------------------------------------------
# Função principal
# ---------------------------------------------------------
def main():
    init_session_state()

    st.sidebar.title("Menu")
    st.sidebar.write(
        "Use o menu abaixo para navegar:\n\n"
        "1. **Custeio variável** – calcula o custo variável por kg.\n"
        "2. **Simulação Monte Carlo** – vê o risco e a variação do resultado.\n"
        "3. **Precificação com markup** – sugere um preço de venda por kg."
    )
    opcao = st.sidebar.radio(
        "Escolha a funcionalidade:",
        (
            "1. Custeio variável",
            "2. Simulação Monte Carlo",
            "3. Precificação com markup",
        )
    )

    if opcao.startswith("1"):
        pagina_custeio_variavel()
    elif opcao.startswith("2"):
        pagina_monte_carlo()
    elif opcao.startswith("3"):
        pagina_precificacao()


if __name__ == "__main__":
    main()
