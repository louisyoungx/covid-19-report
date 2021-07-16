function Submit() {
    let Class = document.getElementsByClassName("glass-input")[0].value;
    let ID = document.getElementsByClassName("glass-input")[1].value;
    let Name = document.getElementsByClassName("glass-input")[2].value;
    let Comment = document.getElementsByClassName("glass-input")[3].value;
    if (Class === "" || ID === "" || Name === "" || Comment === "") {
        Swal.fire({
          type: 'error',
          title: '出错了...',
          text: '请填写完所有字段再提交',
        });
    } else {
        const userid = 1462648167;
        let message = `${Class}班-${ID}号-${Name}: ${Comment}`;
        console.log(message);
        const url = window.location.origin + "/api/changeInfo?message=" + message;
        axios.get(url)
          .then(function (response) {
            console.log(response);
            Swal.fire({
              type: 'success',
              title: '提交成功',
              text: '将会在两到三周内处理',
            });
          })
          .catch(function (error) {
            console.log(error);
            Swal.fire({
              type: 'error',
              title: '出错了...',
              text: error
            });
          });
    }
}
// function thisFunction() {
//     var useless;
// }
// function thisFu() {
// }