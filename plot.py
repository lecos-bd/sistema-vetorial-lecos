import numpy as np
import plotly.graph_objects as go
import data as dt

df_ambiental = dt.tratamento_ambiental()
df_seguranca = dt.tratamento_seguranca()
df_equidade = dt.tratamento_equidade()

def gerar_grafico(estado1, ano1, estado2=None, ano2=None):

    def obter_vetor(estado, ano):
        eq = df_equidade[(df_equidade['Estado'] == estado) & (df_equidade['Ano'] == ano)]['Escala'].sum() or 0
        am = df_ambiental[(df_ambiental['Estado'] == estado) & (df_ambiental['Ano'] == ano)]['Escala'].sum() or 0
        se = df_seguranca[(df_seguranca['Estado'] == estado) & (df_seguranca['Ano'] == ano)]['Escala'].sum() or 0
        return [eq, se, am]

    ideal = [10, 10, 10]
    vetor1 = obter_vetor(estado1, ano1)
    vetor2 = obter_vetor(estado2, ano2) if estado2 and ano2 else None

    # --- TETRAEDRO ---
    def gerar_tetraedro(nome, cor, vetor, opacidade=0.6):
        base = np.array([[0,0,0], [vetor[0],0,0], [0,vetor[1],0], [0,0,vetor[2]]])
        faces = [[0,1,2], [0,1,3], [0,2,3], [1,2,3]]
        x, y, z = base[:,0], base[:,1], base[:,2]

        mesh = go.Mesh3d(
            x=x, y=y, z=z,
            i=[f[0] for f in faces],
            j=[f[1] for f in faces],
            k=[f[2] for f in faces],
            color=cor,
            opacity=opacidade,
            name=nome,
            hoverinfo='skip',
            showscale=False,
            showlegend=False
        )

        # Todos os vértices na legenda (inclui a origem também se quiser)
        pontos = go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=4, color=cor),
            name=f"Vértices {nome}",
            legendgroup=nome,
            showlegend=True,
            hovertemplate=(
                f"{nome}<br>" +
                "x=%{x:.2f}, y=%{y:.2f}, z=%{z:.2f}<extra></extra>"
            )
        )

        return [mesh, pontos]

    # --- VETOR ORIGEM ---
    def adicionar_vetor_origem(nome, cor, vetor):
        # Linha + ponto como um único trace → some junto na legenda
        trace = go.Scatter3d(
            x=[0, vetor[0]], y=[0, vetor[1]], z=[0, vetor[2]],
            mode='lines+markers',
            line=dict(width=6, color=cor),
            marker=dict(size=6, color=cor),
            name=f"{nome}",
            legendgroup=nome,
            showlegend=True,
            hovertemplate=(
                f"{nome}<br>" +
                "x=%{x:.2f}, y=%{y:.2f}, z=%{z:.2f}<extra></extra>"
            )
        )
        return [trace]

    fig = go.Figure()

    # Ideal
    for tr in gerar_tetraedro("Ideal", "lightgray", ideal, opacidade=0.20):
        fig.add_trace(tr)
    for tr in adicionar_vetor_origem("Ideal", "lightgray", ideal):
        fig.add_trace(tr)

    # Estado 1
    for tr in gerar_tetraedro(f"{estado1} {ano1}", "red", vetor1, opacidade=0.30):
        fig.add_trace(tr)
    for tr in adicionar_vetor_origem(f"{estado1} {ano1}", "red", vetor1):
        fig.add_trace(tr)

    # Estado 2 (opcional)
    if vetor2:
        for tr in gerar_tetraedro(f"{estado2} {ano2}", "blue", vetor2, opacidade=0.30):
            fig.add_trace(tr)
        for tr in adicionar_vetor_origem(f"{estado2} {ano2}", "blue", vetor2):
            fig.add_trace(tr)

    # Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, 10], title='Equidade Energética - eixo x'),
            yaxis=dict(range=[0, 10], title='Segurança Energética - eixo y'),
            zaxis=dict(range=[0, 10], title='Meio Ambiente - eixo z'),
            bgcolor="rgba(0,0,0,0)",
        ),
        scene_camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        title=dict(
            text="Comparação de Vetores Trilema",
            font=dict(family="Arial", size=24, color="black"),
            x=0.5, xanchor='center',
        ),
        width=None,
        height=700,
        autosize=True,
        showlegend=True,
        legend=dict(
            x=0, y=0,
            xanchor="left", yanchor="bottom",
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='gray', borderwidth=1
        ),
        margin=dict(l=0, r=0, t=50, b=50)
    )

    # ---- Métricas e ângulos ----
    def angulo(v1, v2):
        v1, v2 = np.array(v1), np.array(v2)
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0
        return np.degrees(np.arccos(np.clip(
            np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)),
            -1, 1
        )))

    eixo_x, eixo_y, eixo_z = [1,0,0], [0,1,0], [0,0,1]
    def formatar_vetor(v): return f"(x={v[0]:.2f}, y={v[1]:.2f}, z={v[2]:.2f})"

    resultado = {
        "vetor_ideal": f"Ideal: {formatar_vetor(ideal)}",
        "vetor_real_1": f"{estado1} {ano1}: {formatar_vetor(vetor1)}",
        "angulo_ideal_1": f"Ângulo entre {estado1} e Ideal: {angulo(vetor1, ideal):.2f}°",
        "angulo_x_1": f"Ângulo entre {estado1} e eixo X: {angulo(vetor1, eixo_x):.2f}°",
        "angulo_y_1": f"Ângulo entre {estado1} e eixo Y: {angulo(vetor1, eixo_y):.2f}°",
        "angulo_z_1": f"Ângulo entre {estado1} e eixo Z: {angulo(vetor1, eixo_z):.2f}°",
    }

    if vetor2:
        resultado.update({
            "vetor_real_2": f"{estado2} {ano2}: {formatar_vetor(vetor2)}",
            "angulo_ideal_2": f"Ângulo entre {estado2} e Ideal: {angulo(vetor2, ideal):.2f}°",
            "angulo_x_2": f"Ângulo entre {estado2} e eixo X: {angulo(vetor2, eixo_x):.2f}°",
            "angulo_y_2": f"Ângulo entre {estado2} e eixo Y: {angulo(vetor2, eixo_y):.2f}°",
            "angulo_z_2": f"Ângulo entre {estado2} e eixo Z: {angulo(vetor2, eixo_z):.2f}°",
        })

    return fig.to_html(full_html=False, include_plotlyjs='cdn'), resultado




def gerar_grafico_radar(estado1, ano1, estado2=None, ano2=None):
    import plotly.express as px

    def obter_vetor(estado, ano):
        eq = df_equidade[(df_equidade['Estado'] == estado) & (df_equidade['Ano'] == ano)]['Escala'].sum() or 0
        am = df_ambiental[(df_ambiental['Estado'] == estado) & (df_ambiental['Ano'] == ano)]['Escala'].sum() or 0
        se = df_seguranca[(df_seguranca['Estado'] == estado) & (df_seguranca['Ano'] == ano)]['Escala'].sum() or 0
        return {"Equidade Energetica - eixo x": eq, "Segurança Energetica - eixo y": se, "Meio Ambiente - eixo z ": am}

    vetor1 = obter_vetor(estado1, ano1)
    vetor2 = obter_vetor(estado2, ano2) if estado2 and ano2 else None

    categorias = list(vetor1.keys())

    fig = go.Figure()

    # Estado 1
    fig.add_trace(go.Scatterpolar(
        r=[vetor1[cat] for cat in categorias],
        theta=categorias,
        fill='toself',
        name=f"{estado1} {ano1}",
        line=dict(color='red')
    ))

    # Estado 2 (se fornecido)
    if vetor2:
        fig.add_trace(go.Scatterpolar(
            r=[vetor2[cat] for cat in categorias],
            theta=categorias,
            fill='toself',
            name=f"{estado2} {ano2}",
            line=dict(color='blue')
        ))

    # Ideal
    ideal = [10, 10, 10]
    fig.add_trace(go.Scatterpolar(
        r=ideal,
        theta=categorias,
        fill='toself',
        name="Ideal (10,10,10)",
        line=dict(color='lightgray', dash='dash')
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10])
    ),
    showlegend=True,
    title="Comparação Trilema (Radar 2D)",
    width=None,
    height=700,
    autosize=True,
    margin=dict(l=20, r=180, t=40, b=20),
    legend=dict(
        x=1.02,
        y=1,
        xanchor="left",
        yanchor="bottom",
        font=dict(size=10),
        bgcolor='rgba(255,255,255,0.5)',
        bordercolor='gray',
        borderwidth=1
    )
)

    return fig.to_html(full_html=False, include_plotlyjs='cdn')