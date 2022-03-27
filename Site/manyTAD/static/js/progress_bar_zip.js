console.log('hello world')
const uploadForm = document.getElementById('upload-form')
const input = document.getElementById('id_file')
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
    fd.append('file', data)
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
                    const percent = e.loaded / e.total * 100
                    console.log(percent)
                    progressBox.innerHTML = `<div class="progress">
                                                <div class="progress-bar" role="progressbar" style="width: ${percent}%" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"></div>
                                            </div>
                                            <p>${percent.toFixed(1)}%</p>`
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
                                    Successfully uploaded the File
                                </div>`
            	nextBtn.classList.remove('not-visible')
            	cancelBox.classList.add('not-visible')
            	window.location.href = response.url
	    }else{
            	alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    File is not a zip or does not match any preivously ran jobs!
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

