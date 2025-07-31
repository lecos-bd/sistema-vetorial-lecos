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

    def gerar_tetraedro(nome, cor, vetor, opacidade=0.6):
        base = np.array([[0,0,0], [vetor[0],0,0], [0,vetor[1],0], [0,0,vetor[2]]])
        faces = [[0,1,2], [0,1,3], [0,2,3], [1,2,3]]
        x, y, z = base[:,0], base[:,1], base[:,2]

        # Tetraedro
        mesh = go.Mesh3d(
            x=x, y=y, z=z,
            i=[f[0] for f in faces],
            j=[f[1] for f in faces],
            k=[f[2] for f in faces],
            color=cor,
            opacity=opacidade,
            name=nome,
            hoverinfo='name',
            showscale=False
        )

        # Vértices (sem origem)
        x_filt, y_filt, z_filt, hovers = [], [], [], []
        for i in range(len(x)):
            if not (x[i] == 0 and y[i] == 0 and z[i] == 0):
                x_filt.append(x[i])
                y_filt.append(y[i])
                z_filt.append(z[i])
                hovers.append(f"{nome}<br>x={x[i]:.2f}, y={y[i]:.2f}, z={z[i]:.2f}")

        pontos = go.Scatter3d(
            x=x_filt, y=y_filt, z=z_filt,
            mode='markers+text',
            marker=dict(size=4, color=cor),
            hovertext=hovers,
            hoverinfo='text',
            name=f"Vértices {nome}"
        )

        return [mesh, pontos]

    fig = go.Figure()

    # Tetraedro Ideal
    for trace in gerar_tetraedro("Ideal", "lightgray", ideal, opacidade=0.245):
        fig.add_trace(trace)

    # Estado 1
    for trace in gerar_tetraedro(f"{estado1} {ano1}", "red", vetor1, opacidade=0.3):
        fig.add_trace(trace)

    # Texto com coordenadas do vetor 1
    fig.add_trace(go.Scatter3d(
        x=[vetor1[0]],
        y=[vetor1[1]],
        z=[vetor1[2]],
        mode='text',
        text=[f"{estado1} {ano1}<br>x: {vetor1[0]:.6f}<br>y: {vetor1[1]:.6f}<br>z: {vetor1[2]:.6f}"],
        textposition='top right',
        textfont=dict(color='black', size=12),
        name=f"Coordenadas {estado1}"
    ))

    # Estado 2 (opcional)
    if vetor2:
        for trace in gerar_tetraedro(f"{estado2} {ano2}", "blue", vetor2, opacidade=0.3):
            fig.add_trace(trace)

        # Texto com coordenadas do vetor 2
        fig.add_trace(go.Scatter3d(
            x=[vetor2[0]],
            y=[vetor2[1]],
            z=[vetor2[2]],
            mode='text',
            text=[f"{estado2} {ano2}<br>x: {vetor2[0]:.6f}<br>y: {vetor2[1]:.6f}<br>z: {vetor2[2]:.6f}"],
            textposition='bottom left',
            textfont=dict(color='black', size=12),
            name=f"Coordenadas {estado2}"
        ))

    # Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, 10], title='Equidade - eixo x'),
            yaxis=dict(range=[0, 10], title='Segurança - eixo y'),
            zaxis=dict(range=[0, 10], title='Ambiental - eixo z'),
            bgcolor="rgba(0,0,0,0)"
        ),
        title="Comparação de Vetores Trilema",
        height=700,
        width=900,
        showlegend=True
    )

    # Cálculo de ângulos
    def angulo(v1, v2):
        v1, v2 = np.array(v1), np.array(v2)
        return np.degrees(np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1)))

    eixo_x, eixo_y, eixo_z = [1,0,0], [0,1,0], [0,0,1]
    def formatar_vetor(v): return f"(x={v[0]:.2f}, y={v[1]:.2f}, z={v[2]:.2f})"

    return fig.to_html(full_html=False, include_plotlyjs='cdn'), {
        "vetor_ideal": f"Ideal: {formatar_vetor(ideal)}",
        "vetor_real": f"{estado1} {ano1}: {formatar_vetor(vetor1)}",
        "angulo_generico_ideal": f"Ângulo entre {estado1} e Ideal: {angulo(vetor1, ideal):.2f}°",
        "angulo_generico_x": f"Ângulo com eixo X: {angulo(vetor1, eixo_x):.2f}°",
        "angulo_generico_y": f"Ângulo com eixo Y: {angulo(vetor1, eixo_y):.2f}°",
        "angulo_generico_z": f"Ângulo com eixo Z: {angulo(vetor1, eixo_z):.2f}°",
    }

def gerar_grafico_radar(estado1, ano1, estado2=None, ano2=None):
    import plotly.express as px

    def obter_vetor(estado, ano):
        eq = df_equidade[(df_equidade['Estado'] == estado) & (df_equidade['Ano'] == ano)]['Escala'].sum() or 0
        am = df_ambiental[(df_ambiental['Estado'] == estado) & (df_ambiental['Ano'] == ano)]['Escala'].sum() or 0
        se = df_seguranca[(df_seguranca['Estado'] == estado) & (df_seguranca['Ano'] == ano)]['Escala'].sum() or 0
        return {"Equidade - eixo x": eq, "Segurança - eixo y": se, "Ambiental - eixo z ": am}

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
        polar=dict(radialaxis = dict(visible=True, range=[0, 10])),
        showlegend=True,
        title="Comparação Trilema (Radar 2D)",
        width=900,  # máximo do CSS
        height=725,
        autosize=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')