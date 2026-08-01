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
// SIGNOS SIMULADOS
// ==========================


function actualizarSignos(){


let pulso=Math.floor(Math.random()*35)+65;

let temp=(36+Math.random()*1.5).toFixed(1);

let oxi=Math.floor(Math.random()*4)+96;

let resp=Math.floor(Math.random()*8)+14;



document.getElementById("pulso").innerHTML=pulso+" BPM";

document.getElementById("temp").innerHTML=temp+" °C";

document.getElementById("oxi").innerHTML=oxi+" %";

document.getElementById("resp").innerHTML=resp+" rpm";



let score=0;



if(pulso>110)
score++;


if(temp>38)
score++;


if(oxi<94)
score+=2;


if(resp>22)
score++;




let estado="ESTABLE";

let color="#00ff99";



if(score>=4){

estado="CRÍTICO";

color="#ff4444";

}

else if(score>=2){

estado="ALERTA";

color="#ffd54a";

}





document.getElementById("iaEstado").innerHTML=estado;

document.getElementById("iaEstado").style.color=color;


document.getElementById("scoreIA").innerHTML=score;



}




actualizarSignos();

setInterval(actualizarSignos,3000);








// ==========================
// BOTONES
// ==========================


function cambiarEstado(estado){


let texto=document.getElementById("estadoTexto");

let dx=document.getElementById("dxIA");



if(estado==="ESTABLE"){


texto.innerHTML="🟢 SISTEMA ESTABLE";

texto.style.color="#00ff99";

dx.innerHTML="Paciente estable";


}



if(estado==="ATENCIÓN"){


texto.innerHTML="🟡 REQUIERE CONTROL";

texto.style.color="#ffd54a";

dx.innerHTML="Monitorización aumentada";


}



if(estado==="CRÍTICO"){


texto.innerHTML="🔴 ALERTA CRÍTICA";

texto.style.color="#ff4444";

dx.innerHTML="Activar protocolo médico";


}



}


function activarSOS(){


let confirmar=confirm(
"¿Activar protocolo de emergencia Jarvice?"
);



if(confirmar){


alert(
"🆘 ALERTA ENVIADA\n\n"+
"Paciente notificado\n"+
"Familia avisada\n"+
"Ubicación compartida"
);


}



}

