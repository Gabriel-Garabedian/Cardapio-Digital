# assim que qeu tento fazer o loguin do chef está dando esse erro 

Erro de tipo
TypeError: o objeto 'builtin_function_or_method' não é iterável.

Rastreamento (chamada mais recente por último)
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 1536 , em__call__
retornar self.wsgi_app(environ, start_response)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 1514 , emwsgi_app
resposta = self.handle_exception(e)
            ^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 1511 , emwsgi_app
resposta = self.full_dispatch_request()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 919 , emfull_dispatch_request
rv = self.handle_user_exception(e)
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 917 , emfull_dispatch_request
rv = self.dispatch_request()
      ^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 902 , emdispatch_request
return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args) # type: ignore[no-any-return]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\app.py" , linha 177 , emw
retornar f(*a,**kw)
        ^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\app.py" , linha 186 , emw
retornar f(*a,**kw)
        ^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\app.py" , linha 375 , emchef_dashboard
return render_template('chef.html', categories=cats, items=items,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\templating.py" , linha 151 , emrender_template
return _render(app, template, context)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\templating.py" , linha 132 , em_render
rv = template.render(context)
      ^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\jinja2\environment.py" , linha 1295 , emrender
self.environment.handle_exception()
 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\jinja2\environment.py" , linha 942 , emhandle_exception
raise rewrite_traceback_stack(source=source)
 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\templates\chef.html" , linha 1 , emtop-level template code
{% estende 'base.html' %}
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\templates\base.html" , linha 66 , emtop-level template code
{% bloco de conteúdo %}{% fim do bloco %}
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\templates\chef.html" , linha 147 , emblock 'content'
{% para oi em og.items %}
TypeError: o objeto 'builtin_function_or_method' não é iterável.
O depurador detectou uma exceção em sua aplicação WSGI. Agora você pode examinar o rastreamento da pilha de chamadas que levou ao erro.
Para alternar entre o rastreamento interativo e o rastreamento em texto simples, clique no título "Rastreamento". A partir do rastreamento em texto simples, você também pode colá-lo. Para executar o código, passe o mouse sobre o frame que deseja depurar e clique no ícone do console no lado direito.

Você pode executar código Python arbitrário nos frames da pilha e existem algumas funções auxiliares extras disponíveis para introspecção:

dump()Mostra todas as variáveis ​​no quadro
dump(obj)despeja tudo o que se sabe sobre o objeto
Apresentado a você por DON'T PANIC , seu amigável interpretador de traceback com tecnologia Werkzeug.

# e quando eu entro em pedidos dentro do loguin do cliente da esse erro 

Erro de tipo
TypeError: o objeto 'builtin_function_or_method' não é iterável.

Rastreamento (chamada mais recente por último)
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 1536 , em__call__
retornar self.wsgi_app(environ, start_response)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 1514 , emwsgi_app
resposta = self.handle_exception(e)
            ^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 1511 , emwsgi_app
resposta = self.full_dispatch_request()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 919 , emfull_dispatch_request
rv = self.handle_user_exception(e)
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 917 , emfull_dispatch_request
rv = self.dispatch_request()
      ^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\app.py" , linha 902 , emdispatch_request
return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args) # type: ignore[no-any-return]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\app.py" , linha 177 , emw
retornar f(*a,**kw)
        ^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\app.py" , linha 322 , emmy_orders
return render_template('my_orders.html', grouped=grouped)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\templating.py" , linha 151 , emrender_template
return _render(app, template, context)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Arquivo "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\flask\templating.py" , linha 132 , em_render
rv = template.render(context)
     ^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\jinja2\environment.py", line 1295, in render
self.environment.handle_exception()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\.venv\Lib\site-packages\jinja2\environment.py", line 942, in handle_exception
raise rewrite_traceback_stack(source=source)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\templates\my_orders.html", line 1, in top-level template code
{% extends 'base.html' %}
File "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\templates\base.html", line 66, in top-level template code
{% block content %}{% endblock %}
File "C:\Users\Antonio Pedro\Downloads\damassa_projeto_v2\damassa\templates\my_orders.html", line 35, in block 'content'
{% for oi in og.items %}
TypeError: 'builtin_function_or_method' object is not iterable
The debugger caught an exception in your WSGI application. You can now look at the traceback which led to the error.
To switch between the interactive traceback and the plaintext one, you can click on the "Traceback" headline. From the text traceback you can also create a paste of it. For code execution mouse-over the frame you want to debug and click on the console icon on the right side.

You can execute arbitrary Python code in the stack frames and there are some extra helpers available for introspection:

dump() shows all variables in the frame
dump(obj) dumps all that's known about the object
Brought to you by DON'T PANIC, your friendly Werkzeug powered traceback interpreter.

# porfavor corrija e antes de me mandar tudo pronto faça uma analise e teste para ver se tudo esta funcionando 