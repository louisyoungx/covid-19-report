var url = window.location.origin + "/api/log";
var content = "";

const ajax = new Promise(function (resolve, reject) {
  axios
    .get(url)
    .then(function (response) {
      content = response.data.data;
      resolve(content);
    })
    .catch(function (error) {
      console.log(error);
      reject(error);
    });
}).then(function (content) {
  console.log(content);
  info = content.split("\n");

  const glassElm = document.getElementById("glass-text");
  // for (let i = 0; i < 100; i++) {
  //   const item = document.createElement('div');
  //     item.id = 'item';
  //     glassElm.appendChild(item);
  // }
  info.reverse(); // 反向迭代
  info.forEach((value, index, array) => {
    let time = value.substring(0, 21);
    let module = value.substring(21).split(":")[0];
    let content = value.substring(21 + module.length);

    let glass_item_list = document.createElement('div');
    glass_item_list.className = 'glass-item-list';

    let item_time = document.createElement('p');
    item_time.className = 'glass-item item-time';
    item_time.innerHTML = time;
    glass_item_list.appendChild(item_time);
    
    let item_module = document.createElement('span');
    item_module.className = 'glass-item item-module';
    item_module.innerHTML = module;
    glass_item_list.appendChild(item_module);

    let item_content = document.createElement('span');
    item_content.className = 'glass-item item-content';
    item_content.innerHTML = content;
    glass_item_list.appendChild(item_content);

    glassElm.appendChild(glass_item_list);
  })
});

// var url = window.location.origin + "/api/log";
// var content = "";
//
// const ajax = new Promise(function (resolve, reject) {
//   axios
//     .get(url)
//     .then(function (response) {
//       content = response.data.data;
//       resolve(content);
//     })
//     .catch(function (error) {
//       console.log(error);
//       reject(error);
//     });
// })


