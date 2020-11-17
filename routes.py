from endpoints.task import create_task, task_summary, detailed_info, list_tasks


def setup_routes(app, cors):
    cors.add(app.router.add_post('/api/v1/task', create_task))
    cors.add(app.router.add_get('/api/v1/all/tasks', list_tasks))
    cors.add(app.router.add_get('/api/v1/task/{id:\d+}/summary', task_summary))
    cors.add(app.router.add_get('/api/v1/job/{id:\d+}', detailed_info))
