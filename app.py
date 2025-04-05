from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_lactancia_app'  # Necesario para usar sesiones

# Añadir datetime a todas las plantillas
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Base de datos de preguntas sobre lactancia materna
PREGUNTAS = [
    {
        "id": 1,
        "pregunta": "¿Es cierto que amamantar es doloroso?",
        "opciones": ["No debería doler si la técnica es correcta", "Sí, siempre es doloroso", "No, nunca causa dolor", "Es doloroso solo el primer mes"],
        "respuesta_correcta": 0,  # Ahora es la opción A
        "explicacion": "La lactancia NO debería ser dolorosa. Si hay dolor, generalmente indica problemas con la posición o el agarre del bebé. Consultar con un profesional de lactancia puede ayudar a corregir la técnica."
    },
    {
        "id": 2,
        "pregunta": "¿Hasta qué edad se recomienda la lactancia materna exclusiva?",
        "opciones": ["Hasta los 3 meses", "Hasta los 6 meses", "Hasta el año", "Solo el primer mes"],
        "respuesta_correcta": 1,  # Sigue siendo la opción B
        "explicacion": "La OMS y UNICEF recomiendan la lactancia materna exclusiva durante los primeros 6 meses de vida, y continuarla junto con alimentación complementaria hasta los 2 años o más."
    },
    {
        "id": 3,
        "pregunta": "Si mi bebé llora mucho, ¿significa que mi leche no es suficiente?",
        "opciones": ["El bebé tiene hambre de fórmula", "Significa que la leche no es nutritiva", "No, el llanto puede tener muchas causas", "Sí, siempre indica falta de leche"],
        "respuesta_correcta": 2,  # Ahora es la opción C
        "explicacion": "El llanto del bebé puede deberse a muchas razones: cólicos, necesidad de contacto, sueño, calor, frío, pañal sucio, etc. No siempre indica hambre o falta de leche materna."
    },
    {
        "id": 4,
        "pregunta": "¿Las madres con pechos pequeños producen menos leche?",
        "opciones": ["Solo producen suficiente el primer mes", "Sí, el tamaño determina la producción", "Depende de la genética", "No, el tamaño no afecta la producción de leche"],
        "respuesta_correcta": 3,  # Ahora es la opción D
        "explicacion": "El tamaño del pecho NO determina la capacidad de producir leche. La producción depende de la frecuencia de las tomas y el vaciado efectivo del pecho, no del tamaño de las mamas."
    },
    {
        "id": 5,
        "pregunta": "¿Es necesario dar agua a los bebés que solo toman leche materna?",
        "opciones": ["No, la leche materna contiene todo el agua que necesitan", "Sí, especialmente en climas cálidos", "Sí, a partir del tercer mes", "Solo si tienen fiebre"],
        "respuesta_correcta": 0,  # Ahora es la opción A
        "explicacion": "La leche materna contiene aproximadamente un 88% de agua, cubriendo todas las necesidades hídricas del bebé hasta los 6 meses, incluso en climas cálidos."
    },
    {
        "id": 6,
        "pregunta": "¿La madre debe seguir una dieta especial durante la lactancia?",
        "opciones": ["Debe comer el doble", "Solo frutas y verduras", "Sí, debe evitar muchos alimentos", "No, puede comer de todo con moderación"],
        "respuesta_correcta": 3,  # Ahora es la opción D
        "explicacion": "La madre lactante puede consumir una dieta variada y equilibrada. Solo se recomendaría evitar algún alimento si se observa que causa molestias al bebé. No es necesario eliminar alimentos preventivamente."
    },
    {
        "id": 7,
        "pregunta": "Si tengo que tomar medicamentos, ¿debo interrumpir la lactancia?",
        "opciones": ["Siempre hay que descansar 24 horas", "La lactancia siempre debe interrumpirse", "No, hay muchos medicamentos compatibles con la lactancia", "Sí, todos los medicamentos pasan a la leche"],
        "respuesta_correcta": 2,  # Ahora es la opción C
        "explicacion": "La mayoría de los medicamentos son compatibles con la lactancia. Siempre consulta con tu médico para que te recete medicamentos seguros durante la lactancia. Existen bases de datos especializadas como e-lactancia.org."
    },
    {
        "id": 8,
        "pregunta": "¿Es cierto que algunas mujeres producen leche de mala calidad?",
        "opciones": ["Solo las madres primerizas", "Depende de la edad de la madre", "Sí, especialmente si tienen mala alimentación", "No, toda leche materna es de buena calidad"],
        "respuesta_correcta": 3,  # Ahora es la opción D
        "explicacion": "Todas las madres producen leche de buena calidad. Incluso en condiciones de desnutrición, el cuerpo prioriza la producción de leche de calidad. La composición varía para adaptarse a las necesidades del bebé."
    },
    {
        "id": 9,
        "pregunta": "¿Los bebés que toman pecho necesitan horarios estrictos de alimentación?",
        "opciones": ["No, se recomienda lactancia a demanda", "Sí, cada 3 horas exactas", "Solo durante la noche", "Sí, máximo 8 tomas diarias"],
        "respuesta_correcta": 0,  # Ahora es la opción A
        "explicacion": "Se recomienda la lactancia a demanda, es decir, alimentar al bebé cuando muestra señales de hambre, sin restricciones de horario o duración. Esto ayuda a establecer una buena producción de leche."
    },
    {
        "id": 10,
        "pregunta": "¿La leche materna previene enfermedades en el bebé?",
        "opciones": ["Solo durante las primeras semanas", "Previene alergias únicamente", "No, solo aporta nutrientes", "Sí, contiene anticuerpos y factores protectores"],
        "respuesta_correcta": 3,  # Ahora es la opción D
        "explicacion": "La leche materna contiene anticuerpos y factores bioactivos que protegen al bebé contra infecciones, alergias y enfermedades crónicas. Esta protección es tanto inmediata como a largo plazo."
    },
    {
        "id": 11,
        "pregunta": "Si mi bebé toma pecho, ¿puedo quedar embarazada?",
        "opciones": ["Imposible durante los primeros 3 meses", "No, la lactancia es un anticonceptivo perfecto", "Solo si das menos de 6 tomas al día", "Sí, es posible aunque estés dando el pecho"],
        "respuesta_correcta": 3,  # Ahora es la opción D
        "explicacion": "Aunque la lactancia exclusiva puede retrasar la ovulación (método MELA), no es un método anticonceptivo 100% eficaz. Se recomienda usar otro método anticonceptivo compatible con la lactancia si se desea evitar el embarazo."
    },
    {
        "id": 12,
        "pregunta": "¿El calostro (primera leche) es importante para el bebé?",
        "opciones": ["Es igual que la leche madura", "Solo si nace prematuro", "Sí, es extremadamente valioso y nutritivo", "No, es mejor esperar a que suba la leche"],
        "respuesta_correcta": 2,  # Ahora es la opción C
        "explicacion": "El calostro es muy valioso: rico en anticuerpos, proteínas y factores de crecimiento. Actúa como la primera inmunización del bebé, protege su sistema digestivo y ayuda a expulsar el meconio (primeras heces)."
    },
    {
        "id": 13,
        "pregunta": "Si tengo los pezones planos o invertidos, ¿podré amamantar?",
        "opciones": ["Solo extrayendo la leche manualmente", "No, es imposible dar el pecho", "Solo con pezoneras permanentes", "Sí, con técnicas y posiciones adecuadas"],
        "respuesta_correcta": 3,  # Ahora es la opción D
        "explicacion": "Los pezones planos o invertidos no impiden la lactancia. El bebé toma el pecho, no solo el pezón. Existen técnicas que ayudan, como la formación del pezón antes de la toma o posiciones específicas."
    },
    {
        "id": 14,
        "pregunta": "¿Es normal que mis pechos produzcan cantidades diferentes de leche?",
        "opciones": ["Sí, es completamente normal", "No, indica un problema", "Indica que uno no funciona bien", "Solo en madres primerizas"],
        "respuesta_correcta": 0,  # Ahora es la opción A
        "explicacion": "Es normal que un pecho produzca más leche que el otro. Cada madre y cada pecho son diferentes. Lo importante es que el bebé esté creciendo adecuadamente."
    },
    {
        "id": 15,
        "pregunta": "Si tengo poca leche, ¿qué debo hacer?",
        "opciones": ["Dar agua entre tomas", "Esperar a que el bebé pida más", "Aumentar la frecuencia de las tomas", "Complementar inmediatamente con fórmula"],
        "respuesta_correcta": 2,  # Ahora es la opción C
        "explicacion": "Para aumentar la producción, lo más efectivo es aumentar la frecuencia de las tomas o extracciones. La producción de leche funciona por oferta y demanda: a mayor estímulo, mayor producción."
    }
]

@app.route('/')
def inicio():
    # Resetear el juego si llega a la página de inicio
    if 'puntaje' in session:
        session.pop('puntaje')
    if 'preguntas_respondidas' in session:
        session.pop('preguntas_respondidas')
    return render_template('inicio.html')

@app.route('/acceder')
def acceder():
    # Asignar un nombre predeterminado a la sesión
    session['nombre'] = 'Usuario'
    # Redirigir al menú
    return redirect(url_for('menu'))

@app.route('/instrucciones')
def instrucciones():
    return render_template('instrucciones.html')

@app.route('/jugar', methods=['GET', 'POST'])
def jugar():
    # Inicializar variables de sesión si no existen
    if 'nombre' not in session:
        return redirect(url_for('inicio'))
    
    if 'puntaje' not in session:
        session['puntaje'] = 0
    
    if 'preguntas_respondidas' not in session:
        session['preguntas_respondidas'] = []
    
    if 'total_preguntas' not in session:
        session['total_preguntas'] = 10  # Número fijo de preguntas para el juego
    
    # Verificar si ya se completaron todas las preguntas
    if len(session['preguntas_respondidas']) >= session['total_preguntas']:
        return redirect(url_for('resultados'))
    
    # Obtener una pregunta que no se haya respondido
    preguntas_disponibles = [p for p in PREGUNTAS if p['id'] not in session['preguntas_respondidas']]
    
    if not preguntas_disponibles:
        return redirect(url_for('resultados'))
    
    pregunta = random.choice(preguntas_disponibles)
    
    # Si el método es POST, procesar la respuesta
    if request.method == 'POST':
        respuesta_usuario = int(request.form.get('respuesta', -1))
        pregunta_id = int(request.form.get('pregunta_id'))
        
        # Buscar la pregunta correspondiente
        for p in PREGUNTAS:
            if p['id'] == pregunta_id:
                pregunta_actual = p
                break
        
        # Verificar si la respuesta es correcta
        if respuesta_usuario == pregunta_actual['respuesta_correcta']:
            session['puntaje'] = session['puntaje'] + 10
            es_correcta = True
        else:
            es_correcta = False
        
        # Marcar esta pregunta como respondida
        preguntas_respondidas = session['preguntas_respondidas']
        preguntas_respondidas.append(pregunta_id)
        session['preguntas_respondidas'] = preguntas_respondidas
        
        # Redireccionar a la página de feedback
        return render_template('feedback.html', 
                              pregunta=pregunta_actual, 
                              respuesta_usuario=respuesta_usuario,
                              es_correcta=es_correcta,
                              puntaje=session['puntaje'],
                              preguntas_respondidas=len(preguntas_respondidas),
                              total_preguntas=session['total_preguntas'])
    
    # Si el método es GET, mostrar una nueva pregunta
    return render_template('pregunta.html', 
                          pregunta=pregunta,
                          num_pregunta=len(session['preguntas_respondidas']) + 1,
                          total_preguntas=session['total_preguntas'])

@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form.get('nombre')
    if nombre.strip():
        session['nombre'] = nombre
        return redirect(url_for('menu'))  # Redirigir al menú en lugar de instrucciones
    else:
        flash('Por favor ingresa un nombre válido', 'error')
        return redirect(url_for('inicio'))

@app.route('/resultados')
def resultados():
    if 'puntaje' not in session:
        return redirect(url_for('inicio'))
    
    puntaje = session['puntaje']
    max_puntaje = session['total_preguntas'] * 10
    porcentaje = (puntaje / max_puntaje) * 100
    
    if porcentaje >= 90:
        mensaje = "¡Excelente! Eres un experto en lactancia materna."
        nivel = "Experto"
    elif porcentaje >= 70:
        mensaje = "¡Muy bien! Tienes buenos conocimientos sobre lactancia materna."
        nivel = "Avanzado"
    elif porcentaje >= 50:
        mensaje = "No está mal, pero aún puedes aprender más sobre lactancia materna."
        nivel = "Intermedio"
    else:
        mensaje = "Necesitas aprender más sobre lactancia materna. ¡No te desanimes!"
        nivel = "Principiante"
    
    # Eliminar la parte que guarda los resultados
    # (ya no se guarda en historial.json)
    
    return render_template('resultados.html', 
                          nombre=session.get('nombre', 'Usuario'),
                          puntaje=puntaje,
                          total=max_puntaje,
                          porcentaje=porcentaje,
                          mensaje=mensaje,
                          nivel=nivel)


# Rutas para el menú principal
@app.route('/menu')
def menu():
    if 'nombre' not in session:
        return redirect(url_for('inicio'))
    return render_template('menu.html')

# Rutas para el juego de memoria
@app.route('/memoria')
def memoria_inicio():
    return render_template('memoria/inicio.html')

@app.route('/memoria/jugar')
def memoria_jugar():
    # Obtener el nivel de dificultad de la URL
    nivel = request.args.get('nivel', 'medio')
    
    # Datos para las tarjetas de memoria
    tarjetas = [
        {"id": 1, "texto": "Calostro", "pareja": 2},
        {"id": 2, "texto": "Primera leche rica en anticuerpos", "pareja": 1},
        {"id": 3, "texto": "Agarre profundo", "pareja": 4},
        {"id": 4, "texto": "Cuando el bebé toma gran parte de la areola", "pareja": 3},
        {"id": 5, "texto": "Oxitocina", "pareja": 6},
        {"id": 6, "texto": "Hormona que provoca la eyección de leche", "pareja": 5},
        {"id": 7, "texto": "Prolactina", "pareja": 8},
        {"id": 8, "texto": "Hormona que estimula la producción de leche", "pareja": 7},
        {"id": 9, "texto": "Lactancia a demanda", "pareja": 10},
        {"id": 10, "texto": "Alimentar al bebé cuando lo pide", "pareja": 9},
        {"id": 11, "texto": "Succión efectiva", "pareja": 12},
        {"id": 12, "texto": "Extracción eficiente de leche por el bebé", "pareja": 11},
        {"id": 13, "texto": "Conductos obstruidos", "pareja": 14},
        {"id": 14, "texto": "Bultos dolorosos por acumulación de leche", "pareja": 13},
        {"id": 15, "texto": "Libre demanda", "pareja": 16},
        {"id": 16, "texto": "Sin horarios ni límites en las tomas", "pareja": 15},
        # Agregar más tarjetas para el nivel difícil
        {"id": 17, "texto": "Leche de transición", "pareja": 18},
        {"id": 18, "texto": "Leche entre el calostro y la madura", "pareja": 17},
        {"id": 19, "texto": "Leche madura", "pareja": 20},
        {"id": 20, "texto": "Leche definitiva rica en grasas", "pareja": 19},
        {"id": 21, "texto": "Mastitis", "pareja": 22},
        {"id": 22, "texto": "Inflamación del tejido mamario", "pareja": 21},
        {"id": 23, "texto": "Posición biológica", "pareja": 24},
        {"id": 24, "texto": "Madre reclinada con bebé sobre el pecho", "pareja": 23},
    ]
    
    return render_template('memoria/juego.html', tarjetas=tarjetas, nivel=nivel)


# Rutas para mitos y realidades
@app.route('/mitos')
def mitos_inicio():
    return render_template('mitos/inicio.html')

@app.route('/mitos/aleatorio')
def mitos_aleatorio():
    # Lista completa de mitos
    mitos = [
        {
            "id": 1,
            "categoria": "Producción de leche",
            "mito": "Si tengo los pechos pequeños, produciré menos leche",
            "realidad": "El tamaño del pecho no determina la capacidad de producir leche. La producción depende principalmente de la frecuencia de las tomas y el vaciado efectivo del pecho. Las mujeres con pechos de cualquier tamaño pueden amamantar exitosamente."
        },
        {
            "id": 2,
            "categoria": "Alimentación materna",
            "mito": "Durante la lactancia debo evitar muchos alimentos",
            "realidad": "La mayoría de las madres pueden comer una dieta variada y equilibrada. Solo en caso de notar que algún alimento específico provoca malestar en el bebé, podría ser necesario eliminarlo temporalmente. No es necesario restringir alimentos preventivamente."
        },
        {
            "id": 3,
            "categoria": "Técnica de lactancia",
            "mito": "Amamantar siempre es doloroso al principio",
            "realidad": "La lactancia no debería ser dolorosa. Si hay dolor persistente, generalmente indica problemas con el agarre o la posición. Un poco de sensibilidad inicial es normal, pero el dolor intenso o prolongado requiere ayuda profesional para corregir la técnica."
        },
        {
            "id": 4,
            "categoria": "Salud del bebé",
            "mito": "Los bebés necesitan agua además de leche materna, especialmente en climas calurosos",
            "realidad": "La leche materna contiene aproximadamente un 88% de agua y satisface todas las necesidades de hidratación del bebé hasta los 6 meses, incluso en climas calurosos. Dar agua antes de los 6 meses puede disminuir la ingesta de leche y los nutrientes que el bebé necesita."
        },
        {
            "id": 5,
            "categoria": "Problemas comunes",
            "mito": "Si el bebé llora mucho, es porque mi leche no es suficiente",
            "realidad": "El llanto puede tener muchas causas: necesidad de contacto, sueño, calor, frío, pañal sucio, cólicos, etc. No siempre indica hambre. Las señales confiables de que el bebé está recibiendo suficiente leche son: 6-8 pañales mojados al día, ganancia adecuada de peso y estar alerta cuando está despierto."
        },
        {
            "id": 6,
            "categoria": "Producción de leche",
            "mito": "Es normal que mis pechos se sientan vacíos después de algunas semanas",
            "realidad": "Después de unas semanas, los pechos se adaptan a la lactancia y pueden sentirse más suaves o menos llenos, incluso cuando la producción de leche es adecuada. Este es un ajuste normal del cuerpo a la demanda de leche del bebé."
        },
        {
            "id": 7,
            "categoria": "Producción de leche",
            "mito": "Si no siento el reflejo de eyección (bajada de leche), no estoy produciendo suficiente",
            "realidad": "No todas las madres sienten la bajada de leche. La ausencia de esta sensación no indica baja producción. Lo importante es que el bebé esté ganando peso adecuadamente y tenga suficientes pañales mojados."
        },
        {
            "id": 8,
            "categoria": "Alimentación materna",
            "mito": "La cerveza aumenta la producción de leche",
            "realidad": "El alcohol en realidad puede disminuir la producción de leche al inhibir el reflejo de eyección. Se recomienda evitar el alcohol durante la lactancia o, si se consume, esperar al menos 2-3 horas por cada bebida antes de amamantar."
        },
        {
            "id": 9,
            "categoria": "Técnica de lactancia",
            "mito": "El bebé debe alimentarse exactamente 10 minutos de cada pecho",
            "realidad": "No hay un tiempo fijo para cada toma. Algunos bebés son eficientes y terminan en minutos, otros pueden tardar más. Lo importante es permitir que el bebé termine completamente un pecho antes de ofrecer el otro."
        },
        {
            "id": 10,
            "categoria": "Salud del bebé",
            "mito": "La leche materna sola no es suficiente después de los 4 meses",
            "realidad": "La OMS recomienda lactancia materna exclusiva durante los primeros 6 meses. La leche materna contiene todos los nutrientes que el bebé necesita durante este período, adaptándose a sus necesidades cambiantes."
        }
    ]
    
    # Seleccionar un mito aleatorio
    mito = random.choice(mitos)
    return render_template('mitos/detalle.html', mito=mito)

# Rutas para posiciones de lactancia
@app.route('/posiciones')
def posiciones_inicio():
    # Lista de posiciones para el menú
    posiciones = [
        {"id": 1, "nombre": "Posición de cuna"},
        {"id": 2, "nombre": "Posición cruzada"},
        {"id": 3, "nombre": "Posición de balón de rugby"},
        {"id": 4, "nombre": "Posición acostada"},
        {"id": 5, "nombre": "Posición biológica"}
    ]
    return render_template('posiciones/inicio.html', posiciones=posiciones)

@app.route('/posiciones/<int:posicion_id>')
def posiciones_detalle(posicion_id):
    # Lista completa de posiciones con detalles
    posiciones = [
        {
            "id": 1, 
            "nombre": "Posición de cuna",
            "imagen": "posicion1.jpg",
            "descripcion": "Es la posición clásica y más común. El bebé está recostado de frente a la madre, con su cabeza apoyada en el antebrazo de la madre del mismo lado que el pecho que está tomando.",
            "beneficios": "Esta posición proporciona buen control de la cabeza del bebé y contacto visual entre madre e hijo. Es cómoda una vez que se ha establecido bien la lactancia.",
            "consejos": "Asegúrate de que la oreja, el hombro y la cadera del bebé estén alineados. Su barriga debe estar en contacto con la tuya (barriga con barriga). Apoya tu brazo en un cojín para mayor comodidad y evitar tensión en la espalda o los hombros."
        },
        {
            "id": 2, 
            "nombre": "Posición cruzada",
            "imagen": "posicion2.jpg",
            "descripcion": "El bebé se sostiene con el brazo contrario al pecho que va a mamar. La madre sujeta la cabeza del bebé colocando la mano en la base del cuello, no en la cabeza.",
            "beneficios": "Proporciona mayor control sobre el agarre del bebé. Ideal para bebés pequeños, prematuros o con dificultades para agarrarse correctamente al pecho. También útil para madres con pechos grandes.",
            "consejos": "Sostén la cabeza del bebé colocando tu mano en la base de su cuello, permitiendo que su cabeza tenga libertad de movimiento. Guía al bebé hacia el pecho, no el pecho hacia el bebé. Esta posición te permite ver bien el agarre."
        },
        {
            "id": 3, 
            "nombre": "Posición de balón de rugby",
            "imagen": "posicion3.jpg",
            "descripcion": "El bebé se coloca debajo del brazo de la madre, con su cuerpo hacia atrás y sus piernas extendidas a lo largo del costado de la madre. La cabeza está a nivel del pecho y frente a él.",
            "beneficios": "Especialmente útil tras una cesárea (evita presión en la herida), para madres con pechos grandes o para amamantar gemelos simultáneamente. También facilita el drenaje de los conductos externos del pecho.",
            "consejos": "Coloca almohadas o cojines bajo el bebé para elevarlo a la altura del pecho. Sostén la cabeza del bebé con la mano del mismo lado que el pecho, sujetando la base del cuello. Asegúrate de que la nariz del bebé está a la altura del pezón antes de que abra la boca."
        },
        {
            "id": 4, 
            "nombre": "Posición acostada",
            "imagen": "posicion4.jpg",
            "descripcion": "La madre y el bebé están acostados de lado, frente a frente. El bebé se ubica a la altura del pecho, con su boca frente al pezón.",
            "beneficios": "Ideal para tomas nocturnas, para madres que han tenido cesárea o episiotomía, o simplemente cuando se está cansada. Favorece el descanso mientras se amamanta y puede ayudar a dormir al bebé.",
            "consejos": "Coloca una almohada detrás de tu espalda y otra entre tus rodillas para mayor comodidad. Puedes poner una toalla enrollada detrás del bebé para mantenerlo en posición. Asegúrate de que el bebé no quede completamente horizontal sino ligeramente inclinado hacia ti."
        },
        {
            "id": 5, 
            "nombre": "Posición biológica",
            "imagen": "posicion5.jpg",
            "descripcion": "La madre se recuesta hacia atrás (semi-reclinada) y el bebé se coloca boca abajo sobre su pecho. Esta posición aprovecha los reflejos naturales del bebé para buscar el pecho.",
            "beneficios": "Utiliza la gravedad y los reflejos naturales del bebé. Reduce la tensión en hombros, brazos y espalda de la madre. Especialmente útil para bebés con dificultades de agarre, con reflejo de eyección fuerte o para madres con pezones planos o invertidos.",
            "consejos": "Reclínate en un ángulo cómodo usando almohadas. Permite que el bebé use sus reflejos naturales para encontrar el pecho por sí mismo. Tu cuerpo sostiene al bebé, así que puedes usar tus manos solo para guiar o ajustar si es necesario. Esta posición funciona mejor con el bebé vestido solo con pañal para favorecer el contacto piel con piel."
        }
    ]
    
    # Buscar la posición seleccionada por ID
    posicion = next((p for p in posiciones if p["id"] == posicion_id), None)
    
    # Si no se encuentra, redirigir al inicio
    if not posicion:
        flash('Posición no encontrada', 'warning')
        return redirect(url_for('posiciones_inicio'))
    
    # Renderizar plantilla con la posición seleccionada
    return render_template('posiciones/detalle.html', posicion=posicion)

@app.route('/posiciones/completa')
def posiciones_completa():
    # Lista completa de posiciones (igual que en posiciones_detalle)
    posiciones = [
        {
            "id": 1, 
            "nombre": "Posición de cuna",
            "imagen": "posicion1.jpg",
            "descripcion": "Es la posición clásica y más común. El bebé está recostado de frente a la madre, con su cabeza apoyada en el antebrazo de la madre del mismo lado que el pecho que está tomando.",
            "beneficios": "Esta posición proporciona buen control de la cabeza del bebé y contacto visual entre madre e hijo. Es cómoda una vez que se ha establecido bien la lactancia.",
            "consejos": "Asegúrate de que la oreja, el hombro y la cadera del bebé estén alineados. Su barriga debe estar en contacto con la tuya (barriga con barriga). Apoya tu brazo en un cojín para mayor comodidad y evitar tensión en la espalda o los hombros."
        },
        {
            "id": 2, 
            "nombre": "Posición cruzada",
            "imagen": "posicion2.jpg",
            "descripcion": "El bebé se sostiene con el brazo contrario al pecho que va a mamar. La madre sujeta la cabeza del bebé colocando la mano en la base del cuello, no en la cabeza.",
            "beneficios": "Proporciona mayor control sobre el agarre del bebé. Ideal para bebés pequeños, prematuros o con dificultades para agarrarse correctamente al pecho. También útil para madres con pechos grandes.",
            "consejos": "Sostén la cabeza del bebé colocando tu mano en la base de su cuello, permitiendo que su cabeza tenga libertad de movimiento. Guía al bebé hacia el pecho, no el pecho hacia el bebé. Esta posición te permite ver bien el agarre."
        },
        {
            "id": 3, 
            "nombre": "Posición de balón de rugby",
            "imagen": "posicion3.jpg",
            "descripcion": "El bebé se coloca debajo del brazo de la madre, con su cuerpo hacia atrás y sus piernas extendidas a lo largo del costado de la madre. La cabeza está a nivel del pecho y frente a él.",
            "beneficios": "Especialmente útil tras una cesárea (evita presión en la herida), para madres con pechos grandes o para amamantar gemelos simultáneamente. También facilita el drenaje de los conductos externos del pecho.",
            "consejos": "Coloca almohadas o cojines bajo el bebé para elevarlo a la altura del pecho. Sostén la cabeza del bebé con la mano del mismo lado que el pecho, sujetando la base del cuello. Asegúrate de que la nariz del bebé está a la altura del pezón antes de que abra la boca."
        },
        {
            "id": 4, 
            "nombre": "Posición acostada",
            "imagen": "posicion4.jpg",
            "descripcion": "La madre y el bebé están acostados de lado, frente a frente. El bebé se ubica a la altura del pecho, con su boca frente al pezón.",
            "beneficios": "Ideal para tomas nocturnas, para madres que han tenido cesárea o episiotomía, o simplemente cuando se está cansada. Favorece el descanso mientras se amamanta y puede ayudar a dormir al bebé.",
            "consejos": "Coloca una almohada detrás de tu espalda y otra entre tus rodillas para mayor comodidad. Puedes poner una toalla enrollada detrás del bebé para mantenerlo en posición. Asegúrate de que el bebé no quede completamente horizontal sino ligeramente inclinado hacia ti."
        },
        {
            "id": 5, 
            "nombre": "Posición biológica",
            "imagen": "posicion5.jpg",
            "descripcion": "La madre se recuesta hacia atrás (semi-reclinada) y el bebé se coloca boca abajo sobre su pecho. Esta posición aprovecha los reflejos naturales del bebé para buscar el pecho.",
            "beneficios": "Utiliza la gravedad y los reflejos naturales del bebé. Reduce la tensión en hombros, brazos y espalda de la madre. Especialmente útil para bebés con dificultades de agarre, con reflejo de eyección fuerte o para madres con pezones planos o invertidos.",
            "consejos": "Reclínate en un ángulo cómodo usando almohadas. Permite que el bebé use sus reflejos naturales para encontrar el pecho por sí mismo. Tu cuerpo sostiene al bebé, así que puedes usar tus manos solo para guiar o ajustar si es necesario. Esta posición funciona mejor con el bebé vestido solo con pañal para favorecer el contacto piel con piel."
        }
    ]
    
    # Renderizar la vista de todas las posiciones
    return render_template('posiciones/completa.html', posiciones=posiciones)



@app.route('/posiciones/juego')
def posiciones_juego():
    posiciones = [
        {"id": 1, "nombre": "Posición de cuna", "imagen": "posicion1.jpg", "descripcion": "El bebé está recostado de frente a la madre, con su cabeza apoyada en el antebrazo.", "consejos": "Alinea la oreja, hombro y cadera del bebé. Mantén al bebé barriga con barriga."},
        {"id": 2, "nombre": "Posición cruzada", "imagen": "posicion2.jpg", "descripcion": "El bebé se sostiene con el brazo contrario al pecho que va a mamar.", "consejos": "Sostén la base del cuello, no la cabeza. Deja que el bebé tenga libertad de movimiento."},
        {"id": 3, "nombre": "Posición de balón de rugby", "imagen": "posicion3.jpg", "descripcion": "El bebé se coloca debajo del brazo, con su cuerpo hacia atrás y piernas extendidas al costado.", "consejos": "Usa almohadas para elevar al bebé. La nariz debe estar a la altura del pezón."},
        {"id": 4, "nombre": "Posición acostada", "imagen": "posicion4.jpg", "descripcion": "Madre y bebé acostados de lado, frente a frente.", "consejos": "Usa almohadas para mayor comodidad. El bebé debe estar ligeramente inclinado hacia ti."},
        {"id": 5, "nombre": "Posición biológica", "imagen": "posicion5.jpg", "descripcion": "Madre semi-reclinada con el bebé boca abajo sobre el pecho.", "consejos": "Aprovecha los reflejos naturales del bebé. El contacto piel con piel facilita el proceso."}
    ]
    return render_template('posiciones/juego.html', posiciones=posiciones)

# Ruta para recursos
@app.route('/recursos')
def recursos():
    return render_template('recursos.html')

# Rutas adicionales para el quiz
@app.route('/quiz/instrucciones')
def quiz_instrucciones():
    if 'nombre' not in session:
        return redirect(url_for('inicio'))
    return render_template('instrucciones.html')

@app.route('/quiz/lactancia')
def quiz_lactancia():
    return redirect(url_for('jugar'))

@app.route('/ranking')
def ranking():
    try:
        with open('static/resultados/historial.json', 'r') as f:
            resultados = json.load(f)
        resultados.sort(key=lambda x: x['puntaje'], reverse=True)
        return render_template('ranking.html', resultados=resultados[:10])
    except:
        return render_template('ranking.html', resultados=[])

if __name__ == '__main__':
    app.run(debug=True)