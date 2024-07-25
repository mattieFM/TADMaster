console.log('hello world')
const uploadForm = document.getElementById('upload-form')
const input = document.getElementById('id_document')
const chromosome = document.getElementById('id_chromosome')
const title  = document.getElementById('id_title')
const description = document.getElementById('id_description')
const email = document.getElementById('id_email')
const resolution = document.getElementById('id_resolution')
var data_input_type = document.getElementsByName('data_input_type')

const alertBox = document.getElementById('alert-box')

const progressBox = document.getElementById('progress-box')
const cancelBox = document.getElementById('cancel-box')
const cancelBtn = document.getElementById('cancel-btn')
const nextBtn = document.getElementById('next-div')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

input.addEventListener('change', ()=>{
    for(i = 0; i < data_input_type.length; i++) {
        if(data_input_type[i].checked){
            data_input_type_val = data_input_type[i].value;
        }
    }
    if (typeof data_input_type_val == 'undefined') {
        alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Please select HIC Data format before uploading a file!
                                </div>`
        uploadForm.reset()
        return;
    }
    progressBox.classList.remove('not-visible')
    cancelBox.classList.remove('not-visible')
    const title_val = title.value
    const description_val = description.value
    const chromosome_val = chromosome.value
    const email_val = email.value
    const resolution_val = resolution.value

    const data = input.files[0]
    const url = URL.createObjectURL(data)
    console.log(data)

    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('document', data)
    fd.append('title', title_val)
    fd.append('description', description_val)
    fd.append('chromosome', chromosome_val)
    fd.append('email', email_val)
    fd.append('resolution', resolution_val)
    fd.append('data_input_type', data_input_type_val)
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
                    if (e.total < 700000000){
                        const percent = e.loaded / e.total * 100
                        console.log(percent)
                        progressBox.innerHTML = `<div class="progress">
                                                    <div class="progress-bar" role="progressbar" style="width: ${percent}%" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"></div>
                                                </div>'
                                                <p>${percent.toFixed(1)}%</p>`
                    } else{
                        xhr.abort()
                        alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Files Must be under 700MB in size. Please use the docker version provided on TADMaster GitHub page to run locally or analyze without a contact matrix.

                                </div>`
                        setTimeout(()=>{
                        uploadForm.reset()
                        progressBox.innerHTML=""
                        alertBox.innerHTML = ""
                        cancelBox.classList.add('not-visible')
                        }, 2000)
                        
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
                }, 2000)
            })
            return xhr
        },
        success: function(response){
            console.log(response)
            if(response.success == 'True'){
            	alertBox.innerHTML = `<div class="alert alert-success" role="alert">
                                    Successfully uploaded the File. Don't refresh the page.
                                </div>`
            	cancelBox.classList.add('not-visible')
            	window.location.href = response.url
	    }else{
            	alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Please fill in all form fields!
                                </div>`
            	uploadForm.reset()
                    progressBox.innerHTML=""
                    cancelBox.classList.add('not-visible')
	    }
        },
        error: function(error){
            console.log(error)
            alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Files Must be under 1GB in size.
                                </div>`
        },
        cache: false,
        contentType: false,
        processData: false,
    })
})

