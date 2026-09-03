// ==========================
// ECG ANIMADO
// ==========================


const canvas=document.getElementById("ecg");


if(canvas){


const ctx=canvas.getContext("2d");


canvas.width=canvas.offsetWidth;

canvas.height=canvas.offsetHeight;



let offset=0;



function dibujarECG(){


ctx.fillStyle="#050b12";

ctx.fillRect(
0,
0,
canvas.width,
canvas.height
);



ctx.strokeStyle="#00ff99";

ctx.lineWidth=2;


ctx.beginPath();



let centro=canvas.height/2;



for(let x=0;x<canvas.width;x++){


let y=centro;


let ciclo=(x+offset)%140;



if(ciclo>20 && ciclo<24)
y-=8;


if(ciclo>35 && ciclo<38)
y+=20;


if(ciclo>38 && ciclo<41)
y-=40;


if(ciclo>41 && ciclo<46)
y+=15;



ctx.lineTo(x,y);



}



ctx.stroke();



offset+=2;



requestAnimationFrame(dibujarECG);



}



dibujarECG();


}

// ==========================
// SIGNOS VITALES REALES
// ==========================

function actualizarSignos() {

    const pulso = document.getElementById("pulso");
    const temp = document.getElementById("temp");
    const oxi = document.getElementById("oxi");
    const resp = document.getElementById("resp");
    const presion = document.getElementById("presion");
    const scoreIA = document.getElementById("scoreIA");
    const iaEstado = document.getElementById("iaEstado");


    // ==========================================
    // OBTENER DATOS ENTREGADOS POR DJANGO
    // ==========================================

    const frecuencia = pulso
        ? pulso.dataset.valor
        : "";

    const temperatura = temp
        ? temp.dataset.valor
        : "";

    const oxigeno = oxi
        ? oxi.dataset.valor
        : "";

    const respiracion = resp
        ? resp.dataset.valor
        : "";

    const presionArterial = presion
        ? presion.dataset.valor
        : "";


    // ==========================================
    // PULSO
    // ==========================================

    if (pulso) {

        if (frecuencia) {
            pulso.innerHTML = frecuencia + " BPM";
        } else {
            pulso.innerHTML = "Sin datos";
        }

    }


    // ==========================================
    // TEMPERATURA
    // ==========================================

    if (temp) {

        if (temperatura) {
            temp.innerHTML = temperatura + " °C";
        } else {
            temp.innerHTML = "Sin datos";
        }

    }


    // ==========================================
    // OXÍGENO
    // ==========================================

    if (oxi) {

        if (oxigeno) {
            oxi.innerHTML = oxigeno + " %";
        } else {
            oxi.innerHTML = "Sin datos";
        }

    }


    // ==========================================
    // RESPIRACIÓN
    // ==========================================

    if (resp) {

        if (respiracion) {
            resp.innerHTML = respiracion + " rpm";
        } else {
            resp.innerHTML = "Sin datos";
        }

    }


    // ==========================================
    // PRESIÓN
    // ==========================================

    if (presion) {

        if (presionArterial) {
            presion.innerHTML = presionArterial;
        } else {
            presion.innerHTML = "Sin datos";
        }

    }


    // ==========================================
    // CONVERSIÓN NUMÉRICA
    // ==========================================

    const pulsoNumero = frecuencia
        ? Number(frecuencia)
        : null;

    const temperaturaNumero = temperatura
        ? Number(temperatura)
        : null;

    const oxigenoNumero = oxigeno
        ? Number(oxigeno)
        : null;


    // ==========================================
    // EVALUACIÓN CLÍNICA BÁSICA
    // ==========================================

    let score = 0;


    if (
        pulsoNumero !== null &&
        (pulsoNumero < 50 || pulsoNumero > 110)
    ) {
        score++;
    }


    if (
        temperaturaNumero !== null &&
        temperaturaNumero > 38
    ) {
        score++;
    }


    if (
        oxigenoNumero !== null &&
        oxigenoNumero < 94
    ) {
        score += 2;
    }


    // ==========================================
    // ESTADO IA
    // ==========================================

    let estado = "ESTABLE";
    let color = "#00ff99";


    if (score >= 3) {

        estado = "CRÍTICO";
        color = "#ff4444";

    }

    else if (score >= 1) {

        estado = "ATENCIÓN";
        color = "#ffd54a";

    }


    if (iaEstado) {

        iaEstado.innerHTML = estado;
        iaEstado.style.color = color;

    }


    if (scoreIA) {

        scoreIA.innerHTML = score;

    }

}


// ==========================================
// EJECUTAR AL CARGAR
// ==========================================

actualizarSignos();

function cambiarEstado(estado) {

    const texto = document.getElementById("estadoTexto");
    const dx = document.getElementById("dxIA");

    // ==========================================
    // TRADUCIR ESTADO VISUAL → ESTADO DEL MODELO
    // ==========================================

    let estadoBackend;

    if (estado === "ESTABLE") {
        estadoBackend = "OK";
    }
    else if (estado === "ATENCIÓN") {
        estadoBackend = "CANSADO";
    }
    else if (estado === "CRÍTICO") {
        estadoBackend = "CRITICO";
    }
    else {
        console.error("Estado no reconocido:", estado);
        return;
    }

    // ==========================================
    // ACTUALIZAR INTERFAZ
    // ==========================================

    if (estado === "ESTABLE") {

        if (texto) {
            texto.innerHTML = "🟢 SISTEMA ESTABLE";
            texto.style.color = "#00ff99";
        }

        if (dx) {
            dx.innerHTML = "Paciente estable";
        }

    }

    else if (estado === "ATENCIÓN") {

        if (texto) {
            texto.innerHTML = "🟡 REQUIERE CONTROL";
            texto.style.color = "#ffd54a";
        }

        if (dx) {
            dx.innerHTML = "Monitorización aumentada";
        }

    }

    else if (estado === "CRÍTICO") {

        if (texto) {
            texto.innerHTML = "🔴 ALERTA CRÍTICA";
            texto.style.color = "#ff4444";
        }

        if (dx) {
            dx.innerHTML = "Activar protocolo médico";
        }

    }

    // ==========================================
    // VERIFICAR PACIENTE ACTIVO
    // ==========================================

    const pacienteId = window.JARVICE_PACIENTE_ID;

    if (!pacienteId) {

        console.warn(
            "Jarvice: no hay paciente activo asociado al usuario."
        );

        return;
    }

    // ==========================================
    // ENVIAR ESTADO A DJANGO
    // ==========================================

    fetch(`/api/cambiar-estado/${pacienteId}/?estado=${estadoBackend}`, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })

    .then(response => {

        if (!response.ok) {
            throw new Error(
                `Error HTTP ${response.status}`
            );
        }

        return response.json();
    })

    .then(data => {

        if (!data.ok) {

            console.error(
                "Jarvice: Django rechazó el cambio de estado.",
                data
            );

            return;
        }

        console.log(
            "Jarvice: estado actualizado correctamente.",
            data
        );

    })

    .catch(error => {

        console.error(
            "Jarvice: error comunicando con Django:",
            error
        );

    });

}
