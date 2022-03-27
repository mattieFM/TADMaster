const data_input_type = JSON.parse(document.getElementById('data_input_type').textContent);
console.log(data_input_type)
const uploadForm = document.getElementById('upload-form')
const input = document.getElementById('id_document')
console.log(uploadForm)
console.log(input)

const alertBox = document.getElementById('alert-box')

const progressBox = document.getElementById('progress-box')
const cancelBox = document.getElementById('cancel-box')
const cancelBtn = document.getElementById('cancel-btn')
const nextBtn = document.getElementById('next-div')
const csrf = document.getElementsByName('csrfmiddlewaretoken')
input.addEventListener('change', ()=>{
    progressBox.classList.remove('not-visible')
    cancelBox.classList.remove('not-visible')

    const data = input.files[0]
    const url = URL.createObjectURL(data)
    console.log(data)

    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('document', data)
    $.ajax({
        type:'POST',
        url: uploadForm.action,
        enctype: 'multipart/form-data',
        data: fd,
        beforeSend: function(){
            console.log('before')
            alertBox.innerHTML= ""

        },
        xhr: function(){
            const xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener('progress', e=>{
                // console.log(e)
                if (e.lengthComputable) {
                    if (data_input_type == 'sparse' || data_input_type == 'square') {
                        if (e.total < 250000000){
                            const percent = e.loaded / e.total * 100
                            console.log(percent)
                            progressBox.innerHTML = `<div class="progress">
                                                    <div class="progress-bar" role="progressbar" style="width: ${percent}%" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"></div>
                                                    </div>'
                                                    <p>${percent.toFixed(1)}%</p>`
                        } else{
                            xhr.abort()
                            alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                                   Square or sparse matrix files must be under 250MB in size.
                                                  </div>`
                            setTimeout(()=>{
                            uploadForm.reset()
                            progressBox.innerHTML=""
                            alertBox.innerHTML = ""
                            cancelBox.classList.add('not-visible')
                            }, 2000)
                          }   
                } else{
                    if (e.total < 500000000){
                        const percent = e.loaded / e.total * 100
                        console.log(percent)
                        progressBox.innerHTML = `<div class="progress">
                                                    <div class="progress-bar" role="progressbar" style="width: ${percent}%" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"></div>
                                                </div>'
                                                <p>${percent.toFixed(1)}%</p>`
                    } else{
                        xhr.abort()
                        alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Non sparse or squareFiles must be under 500MB in size.
                                </div>`
                        setTimeout(()=>{
                        uploadForm.reset()
                        progressBox.innerHTML=""
                        alertBox.innerHTML = ""
                        cancelBox.classList.add('not-visible')
                        }, 5000)
                     }   
                 }
               }
            })
            cancelBtn.addEventListener('click', ()=>{
                xhr.abort()
                setTimeout(()=>{
                    uploadForm.reset()
                    progressBox.innerHTML=""
                    alertBox.innerHTML = ""
                    cancelBox.classList.add('not-visible')
                }, 5000)
            })
            return xhr
        },
        success: function(response){
            console.log(response)
            if(response.success == 'True'){
            	alertBox.innerHTML = `<div class="alert alert-success" role="alert">
                                    Successfully uploaded the File
                                </div>`
            	cancelBox.classList.add('not-visible')
            	window.location.href = response.url
	    }else{
            	alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Files Must be under 1GB in size.
                                </div>`
            	uploadForm.reset()
                progressBox.innerHTML=""
                cancelBox.classList.add('not-visible')
	    }
        },
        error: function(error){
            console.log(error)
            alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Oops... something went wrong
                                </div>`
        },
        cache: false,
        contentType: false,
        processData: false,
    })
})

