
function createHttpRequest()
{
    var xmlHttp=null;
    try{
        // Firefox, Opera 8.0+, Safari
        xmlHttp=new XMLHttpRequest();
    }catch (e){
        // Internet Explorer
        try{
            xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
        }catch (e){
            try{
                xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
            }catch (e){
                alert("您的浏览器不支持AJAX！");
            }
        }
    }
    return xmlHttp;
}

function uploadFileToServer(){
    var uploadFile = document.getElementById("upload_file_id");
    var uploadTip = document.getElementById("upload_tip_id");
    var uploadProgress = document.getElementById("upload_progress_id");

    if(uploadFile.value==""){
        uploadTip.innerText="请选择一个文件";
    }else if(uploadFile.files[0].size>1024 &&uploadFile.files[0].size<(40*1024*1024)){
        try{
            if(window.FileReader){
                var fReader = new FileReader();
                var xhreq=createHttpRequest();
                xhreq.onreadystatechange=function(){
                    if(xhreq.readyState==4){
                        if(xhreq.status==200){
                            uploadTip.innerText="文件上传成功";
                            // setTimeout(function(){
                            //     hideUploadDialog()
                            // },2000);	//2秒后隐藏
                        }else{
                            uploadTip.innerText="文件上传失败了";
                        }
                    }
                }
                fReader.οnlοad=function(e){
                    xhreq.open("POST","/upload/file",true);
                    xhreq.setRequestHeader("Content-type", "application/octet-stream"); //流类型
                    xhreq.setRequestHeader("Content-length", fwFile.files[0].size);     //文件大小
                    xhreq.setRequestHeader("uploadfile_name", encodeURI(fwFile.files[0].name)); //兼容中文
                    xhreq.send(fReader.result);
                }
                fReader.onprogress = function(e){
                    uploadProgress.value = e.loaded*100/e.total;
                }
                fReader.readAsArrayBuffer(uploadFile.files[0]);
                uploadProgress.style.visibility="visible";
                uploadProgress.value = 0;
            }else{
                uploadTip.innerText="浏览器不支持上传文件";
            }
        }catch(e){
            uploadTip.innerText="文件上传失败";
        }
    }else{
        uploadTip.innerText="文件不符合要求";
    }
}
// function showUploadDialog(){
//     var up_dialog=document.getElementById("upload_dialog");
//     document.getElementById("upload_tip_id").innerText="请选择要上传的文件";
//     document.getElementById("upload_progress_id").style.visibility="hidden";
//     up_dialog.style.visibility="visible";
//
// }
// function hideUploadDialog(){
//     var up_dialog=document.getElementById("upload_dialog");
//     document.getElementById("upload_progress_id").style.visibility="hidden";
//     up_dialog.style.visibility="hidden";
// }
