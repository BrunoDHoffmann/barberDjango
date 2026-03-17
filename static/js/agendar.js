// Pega todos os checkboxes de serviço
const checkboxesServicos = document.querySelectorAll('input[name="servicos"]')

// Pega o select do barbeiro
const barbeirSelect = document.getElementById('barbeiro')

// Container onde vamos exibir os horários
const horariosContainer = document.getElementById('horarios-container')

// Campos hidden que serão enviados no POST
const dataInput = document.getElementById('data-selecionada')
const horaInput = document.getElementById('hora-selecionada')


// ── Calcula a duração total dos serviços marcados ──
function calcularDuracaoTotal() {
    let total = 0
    checkboxesServicos.forEach(checkbox => {
        if (checkbox.checked) {
            // lê o atributo data-duracao de cada checkbox marcado
            total += parseInt(checkbox.dataset.duracao)
        }
    })
    return total
}


// ── Busca os horários disponíveis na view Django ──
function buscarHorarios() {
    const barbeiroId = barbeirSelect.value
    const duracao = calcularDuracaoTotal()

    // Só busca se tiver barbeiro selecionado e pelo menos 1 serviço marcado
    if (!barbeiroId || duracao === 0) {
        horariosContainer.innerHTML = '<p class="text-muted">Selecione um barbeiro e pelo menos um serviço.</p>'
        return
    }

    horariosContainer.innerHTML = '<p class="text-muted">Buscando horários disponíveis...</p>'
    dataInput.value = ''
    horaInput.value = ''

    // Envia o id do barbeiro e a duração para a view
    fetch(`/agendar/?barbeiro_id=${barbeiroId}&duracao=${duracao}`)
        .then(response => response.json())
        .then(data => {
            if (data.dias.length === 0) {
                horariosContainer.innerHTML = '<p class="text-muted">Nenhum horário disponível nas próximas duas semanas.</p>'
                return
            }
            renderizarHorarios(data.dias)
        })
}


// ── Renderiza os cards de datas e horários ──
function renderizarHorarios(dias) {
    let html = ''
    dias.forEach(dia => {
        html += `
            <div class="card" style="margin-bottom:12px">
                <p style="margin-bottom:10px">
                    <strong class="text-gold">${dia.dia_semana}</strong>
                    <span class="text-muted"> — ${dia.data_exibicao}</span>
                </p>
                <div>
                    ${dia.horarios.map(horario => `
                        <button
                            type="button"
                            class="btn btn-secondary horario-btn"
                            onclick="selecionarHorario(this, '${dia.data}', '${horario}')"
                        >
                            ${horario}
                        </button>
                    `).join('')}
                </div>
            </div>
        `
    })
    horariosContainer.innerHTML = html
}


// ── Marca o horário selecionado e preenche os campos hidden ──
function selecionarHorario(btn, data, horario) {
    // Remove seleção anterior
    document.querySelectorAll('.horario-btn').forEach(b => {
        b.classList.remove('btn-selected')
        b.classList.add('btn-secondary')
    })

    // Marca o botão clicado
    btn.classList.remove('btn-secondary')
    btn.classList.add('btn-selected')

    // Preenche os campos hidden
    dataInput.value = data
    horaInput.value = horario
}


// ── Monitora mudanças nos checkboxes e no select do barbeiro ──
checkboxesServicos.forEach(checkbox => {
    checkbox.addEventListener('change', buscarHorarios)
})

barbeirSelect.addEventListener('change', buscarHorarios)