/* Javascript for LoginXBlock. */
function LoginXBlock(runtime, element) {
    Create_result.text("");
    AutoLogin_result.text("");
    AutoLogin_url.text("");

    $('#submit', element).bind('click', function () {
        var Student_id = $('#email').val();
        var Lastname = $('#lastname').val();
        var Firstname = $('#firstname').val();

        var Autologin = $('#autologin').prop("checked");
        var CreateStudent = $('#createStudent').prop("checked");

        var Create_result = $('#create_result');
        var AutoLogin_result = $('#autoLogin_result');
        var AutoLogin_url = $('#autoLogin_url #url');

        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'autoLogIn'),
            data: JSON.stringify({
                student_id: Student_id,
                lastname: Lastname,
                firstname: Firstname,

                autoLogin: Autologin,
                createStudent: CreateStudent
            }),
            success: function (result) {
                Create_result.text(result.autoLogin_result);
                AutoLogin_result.text(result.create_result);
                if (result.autoLogin_url != '') {
                    AutoLogin_url.text("");
                    AutoLogin_url.append("click here");
                    AutoLogin_url.attr("href", result.autoLogin_url);
                } else {
                    AutoLogin_url.text("");

                }
            }
        });
    });

}
