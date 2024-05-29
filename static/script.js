document.getElementById('consultaForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const nit = document.getElementById('nit').value;
    const loader = document.getElementById('loader');
    const resultado = document.getElementById('resultado');

    // Mostrar el indicador de carga
    loader.style.display = 'block';
    resultado.innerText = '';
    resultado.classList.remove('success', 'error');

    fetch('/consulta', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nit: nit }),
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'resultado.json';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        resultado.innerText = 'Consulta Exitosa';
        resultado.classList.add('success');
    })
    .catch(error => {
        console.error('Error:', error);
        resultado.innerText = 'Error al realizar la consulta';
        resultado.classList.add('error');
    })
    .finally(() => {
        // Ocultar el indicador de carga
        loader.style.display = 'none';
    });
});