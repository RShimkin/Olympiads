let editor

window.onload = function () {

    const langs = {
        'C#': 'text/x-c++src',
        'C++': 'text/x-c++src'
    }

    document.querySelector('#div_id_plang').className += ' choiceField'
    
    //const curtitle = document.querySelector('#id_title').value
    const lang = document.querySelector('#id_plang').value
    //const ta = document.querySelector('#ta')
    const sb = document.querySelector('.sb')
    const panel = document.querySelector('#panel')
    sb.addEventListener('click', (e) => {
        const form = document.forms[0]
        const fd = new FormData(form)
        console.log(fd)
        //ta.value = ta.value.replaceAll("\r","")
        e.preventDefault()

        document.querySelector('#ta').value = editor.getValue()

        panel.innerText = "Ожидание результата..."
        panel.className = "bg-secondary p-3 text-white"

        $.ajax({
            data: $(form).serialize(), 
            type: 'POST', // GET or POST
            url: location.href,
            success: function (resp) {
                console.log("Получено")
                console.log(resp)
                if (resp.cerror) {
                    panel.innerText = `Ошибки компиляции: ${resp.cerror}`
                    panel.className = "bg-danger p-3 text-white"
                }
                else if (resp.err) {
                    panel.innerText = `Ошибки выполнения: ${resp.err}`
                    panel.className = "bg-danger p-3 text-white"
                }
                else {
                    panel.innerText = `Программа успешно отработала, набрано ${resp.score} баллов`
                    elem = document.querySelector('#rating_table')
                    elem.innerHTML = resp.table
                    $('#rating_table').html(resp.table)
                    panel.className = "bg-success p-3 text-white"
                }
            },
            error: function (resp) {
                console.log("Ошибка")
                panel.innerText = "доставлено с ошибками"
            }
        })

        /*
        fetch(location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8' // x-www-form-urlencoded
            },
            body: JSON.stringify(data)
        }).then(resp => console.log(resp)) */
    })

    editor = CodeMirror.fromTextArea(document.getElementById("ta"), {
        styleActiveLine: true,
        lineNumbers: true,
        matchBrackets: true, 
        mode: 'text/x-c++src',
        indentUnit: 4,
        theme: 'dracula',
        scrollbarStyle: 'overlay'
        //value: "#include <iostream>\n\nusing namespace std\n\nint main(int argc, *char[] argv){\nreturn0\n};"
    }); 

    $('#id_plang').on('change', (e) => {
        //editor.setOption("mode", this.value)
        let val = $('#id_plang').val()
        console.log(val)
        editor.toTextArea()
        editor = CodeMirror.fromTextArea(document.getElementById("ta"), {
            styleActiveLine: true,
            lineNumbers: true,
            matchBrackets: true, 
            mode: langs[val],
            indentUnit: 4,
            theme: 'dracula',
            scrollbarStyle: 'overlay'
        });
    })
}