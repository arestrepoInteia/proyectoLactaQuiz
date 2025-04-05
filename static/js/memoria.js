document.addEventListener('DOMContentLoaded', function() {
    // Obtener datos de tarjetas de la variable global
    const tarjetasData = window.tarjetasData;
    
    // Elementos DOM
    const tableroJuego = document.getElementById('tableroJuego');
    const tiempoElement = document.getElementById('tiempo');
    const movimientosElement = document.getElementById('movimientos');
    const juegoCompletadoAlert = document.getElementById('juegoCompletado');
    const tiempoFinalElement = document.getElementById('tiempoFinal');
    const movimientosFinalElement = document.getElementById('movimientosFinal');
    const reiniciarBtn = document.getElementById('reiniciarBtn');
    const jugarNuevoBtn = document.getElementById('jugarNuevoBtn');
    const ayudaBtn = document.getElementById('ayudaBtn');
    
    // Variables del juego
    let tarjetasJuego = [];
    let tarjetasSeleccionadas = [];
    let movimientos = 0;
    let parejasEncontradas = 0;
    let tiempoTranscurrido = 0;
    let timerInterval;
    let juegoIniciado = false;
    
    // Modal de ayuda
    const ayudaModal = new bootstrap.Modal(document.getElementById('ayudaModal'));
    
    // Función para obtener parámetros de la URL
    function getParametroURL(nombre) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(nombre);
    }
    
    // Inicializar juego
    function inicializarJuego() {
        // Restablecer variables
        tarjetasSeleccionadas = [];
        movimientos = 0;
        parejasEncontradas = 0;
        tiempoTranscurrido = 0;
        juegoIniciado = false;
        
        // Actualizar UI
        tiempoElement.textContent = '00:00';
        movimientosElement.textContent = '0';
        juegoCompletadoAlert.classList.add('d-none');
        
        // Detener timer si está activo
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        
        // Preparar tarjetas para el juego
        prepararTarjetas();
        
        // Crear tablero
        crearTablero();
    }
    
    function prepararTarjetas() {
        // Obtener el nivel de dificultad de la URL
        const nivel = getParametroURL('nivel') || 'medio';
        
        // Determinar cuántas TARJETAS TOTALES mostrar según el nivel
        let numTarjetasTotales = 16; // Valor por defecto (nivel medio)
        
        if (nivel === 'facil') {
            numTarjetasTotales = 8;  // 8 tarjetas = 4 parejas
        } else if (nivel === 'dificil') {
            numTarjetasTotales = 24; // 24 tarjetas = 12 parejas
        }
        
        console.log(`Nivel: ${nivel}, Tarjetas totales: ${numTarjetasTotales}`);
        
        // Crear un array con todas las parejas disponibles
        let parejas = [];
        let parejasMap = new Map();
        
        // Agrupar las tarjetas por parejas
        tarjetasData.forEach(tarjeta => {
            const min = Math.min(tarjeta.id, tarjeta.pareja);
            const max = Math.max(tarjeta.id, tarjeta.pareja);
            const key = `${min}-${max}`;
            
            if (!parejasMap.has(key)) {
                parejasMap.set(key, [tarjeta]);
            } else {
                parejasMap.get(key).push(tarjeta);
            }
        });
        
        // Convertir el mapa a un array de parejas
        parejasMap.forEach(value => {
            if (value.length === 2) {
                parejas.push(value);
            }
        });
        
        console.log(`Número total de parejas disponibles: ${parejas.length}`);
        
        // Limitar según el nivel de dificultad (numTarjetasTotales/2 = número de parejas)
        const numParejas = numTarjetasTotales / 2;
        parejas = parejas.slice(0, numParejas);
        
        console.log(`Parejas seleccionadas: ${parejas.length}`);
        
        // Crear el array final de tarjetas aplanando el array de parejas
        tarjetasJuego = parejas.flat();
        
        console.log(`Tarjetas finales para jugar: ${tarjetasJuego.length}`);
        
        // Mezclar tarjetas
        mezclarTarjetas(tarjetasJuego);
    }
    
    function mezclarTarjetas(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
    
    function crearTablero() {
        // Limpiar tablero
        tableroJuego.innerHTML = '';
        
        // Obtener nivel actual
        const nivel = getParametroURL('nivel') || 'medio';
        
        // Ajustar estilos del tablero según el nivel
        tableroJuego.className = `memoria-tablero mb-4 ${nivel}`;
        
        // Configurar columnas según el nivel
        if (nivel === 'dificil') {
            // Para nivel difícil, usamos 6 columnas para 24 tarjetas
            tableroJuego.style.gridTemplateColumns = 'repeat(6, 1fr)';
        } else if (nivel === 'facil') {
            // Para nivel fácil, usamos 4 columnas para 8 tarjetas (2 filas de 4)
            tableroJuego.style.gridTemplateColumns = 'repeat(4, 1fr)';
        } else {
            // Para nivel medio, usamos 4 columnas para 16 tarjetas (4 filas de 4)
            tableroJuego.style.gridTemplateColumns = 'repeat(4, 1fr)';
        }
        
        // Crear tarjetas
        tarjetasJuego.forEach((tarjeta, index) => {
            const cartaElement = document.createElement('div');
            cartaElement.className = 'memoria-carta';
            cartaElement.dataset.id = tarjeta.id;
            cartaElement.dataset.pareja = tarjeta.pareja;
            cartaElement.dataset.index = index;
            
            cartaElement.innerHTML = `
                <div class="memoria-carta-inner">
                    <div class="memoria-carta-front">
                        <i class="bi bi-droplet-half fs-1"></i>
                    </div>
                    <div class="memoria-carta-back">
                        <p>${tarjeta.texto}</p>
                    </div>
                </div>
            `;
            
            // Agregar evento de clic
            cartaElement.addEventListener('click', function() {
                voltearTarjeta(this);
            });
            
            tableroJuego.appendChild(cartaElement);
        });
    }
    
    function voltearTarjeta(carta) {
        // No hacer nada si la carta ya está volteada o hay dos cartas seleccionadas
        if (carta.classList.contains('flipped') || tarjetasSeleccionadas.length >= 2) {
            return;
        }
        
        // Iniciar timer en el primer clic
        if (!juegoIniciado) {
            iniciarTimer();
            juegoIniciado = true;
        }
        
        // Voltear carta
        carta.classList.add('flipped');
        
        // Agregar a seleccionadas
        tarjetasSeleccionadas.push(carta);
        
        // Si tenemos dos cartas seleccionadas, verificar si son pareja
        if (tarjetasSeleccionadas.length === 2) {
            movimientos++;
            movimientosElement.textContent = movimientos;
            
            const carta1 = tarjetasSeleccionadas[0];
            const carta2 = tarjetasSeleccionadas[1];
            
            if (carta1.dataset.id === carta2.dataset.pareja && carta2.dataset.id === carta1.dataset.pareja) {
                // Son pareja
                setTimeout(() => {
                    carta1.classList.add('matched');
                    carta2.classList.add('matched');
                    tarjetasSeleccionadas = [];
                    
                    parejasEncontradas++;
                    
                    // Verificar si se completó el juego
                    if (parejasEncontradas === tarjetasJuego.length / 2) {
                        finalizarJuego();
                    }
                }, 500);
            } else {
                // No son pareja
                setTimeout(() => {
                    carta1.classList.remove('flipped');
                    carta2.classList.remove('flipped');
                    tarjetasSeleccionadas = [];
                }, 1000);
            }
        }
    }
    
    function iniciarTimer() {
        timerInterval = setInterval(() => {
            tiempoTranscurrido++;
            actualizarTiempoUI();
        }, 1000);
    }
    
    function actualizarTiempoUI() {
        const minutos = Math.floor(tiempoTranscurrido / 60);
        const segundos = tiempoTranscurrido % 60;
        tiempoElement.textContent = `${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
    }
    
    function finalizarJuego() {
        // Detener timer
        clearInterval(timerInterval);
        
        // Actualizar UI
        tiempoFinalElement.textContent = tiempoElement.textContent;
        movimientosFinalElement.textContent = movimientos;
        juegoCompletadoAlert.classList.remove('d-none');
        
        // Guardar resultado (podría implementarse envío al servidor)
        guardarResultado();
    }
    
    function guardarResultado() {
        // En una implementación real, esto enviaría los datos al servidor
        console.log('Juego completado:', {
            tiempo: tiempoTranscurrido,
            movimientos: movimientos,
            nivel: getParametroURL('nivel') || 'medio'
        });
    }
    
    // Eventos
    reiniciarBtn.addEventListener('click', inicializarJuego);
    jugarNuevoBtn.addEventListener('click', inicializarJuego);
    ayudaBtn.addEventListener('click', function() {
        ayudaModal.show();
    });
    
    // Iniciar juego
    inicializarJuego();
});