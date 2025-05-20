function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}


const tasks = document.querySelectorAll('.task');
const columns = document.querySelectorAll('.column');

tasks.forEach(task => {
    task.addEventListener('dragstart', () => {
        task.classList.add('dragging');
    });

    task.addEventListener('dragend', () => {
        task.classList.remove('dragging');
    });
});

columns.forEach(column => {
    column.addEventListener('dragover', (e) => {
        e.preventDefault();
        column.classList.add('over');
    });

    column.addEventListener('dragleave', () => {
        column.classList.remove('over');
    });
    
    column.addEventListener('drop', (event) => {
        event.preventDefault(); // предотвращаем стандартное поведение
    
        const draggingTask = document.querySelector('.dragging');
        const moveadd = column.querySelector('.list_title');
        column.prepend(draggingTask);
        column.prepend(moveadd);
        column.classList.remove('over');
    
        // Получаем данные из dataTransfer
        var taskId = event.dataTransfer.getData("taskId");
        var newListId = column.dataset.listId; // используем dataset для получения нового ID списка
        var oldListId = event.dataTransfer.getData("oldListId");
    
        // Отправляем запрос на сервер
        fetch('/project/' + project_id + '/update-task-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: 'task_id=' + taskId + '&list_id=' + newListId + '&old_list_id=' + oldListId,
        });
    });
});



function allowDrop(event) {
    event.preventDefault();
}

document.addEventListener("dragstart", function(event) {
    event.dataTransfer.setData("oldListId", event.target.parentElement.dataset.listId)
    event.dataTransfer.setData("taskId", event.target.dataset.taskId);
});


