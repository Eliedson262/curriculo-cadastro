from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'souza-conecta-chave-secreta-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///curriculos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs('uploads/fotos', exist_ok=True)
os.makedirs('uploads/curriculos', exist_ok=True)
os.makedirs('output', exist_ok=True)

db = SQLAlchemy(app)


class Curriculo(db.Model):
    __tablename__ = 'curriculo'

    id                 = db.Column(db.Integer, primary_key=True, autoincrement=True)
    protocolo          = db.Column(db.String(50),  nullable=True)
    tipo               = db.Column(db.String(50),  nullable=True)
    nome               = db.Column(db.String(150), nullable=True)
    email              = db.Column(db.String(150), nullable=True)
    telefone           = db.Column(db.String(30),  nullable=True)
    idade              = db.Column(db.String(10),  nullable=True)
    cidade             = db.Column(db.String(100), nullable=True)
    estado             = db.Column(db.String(50),  nullable=True)
    linkedin           = db.Column(db.String(200), nullable=True)
    pretensao          = db.Column(db.String(50),  nullable=True)
    objetivo           = db.Column(db.Text,        nullable=True)
    escolaridade       = db.Column(db.String(100), nullable=True)
    curso_grad         = db.Column(db.String(150), nullable=True)
    instituicao        = db.Column(db.String(150), nullable=True)
    ano_conclusao      = db.Column(db.String(20),  nullable=True)
    hard_skills        = db.Column(db.Text,        nullable=True)
    soft_skills        = db.Column(db.Text,        nullable=True)
    certificacoes      = db.Column(db.Text,        nullable=True)
    projetos           = db.Column(db.Text,        nullable=True)
    experiencia        = db.Column(db.String(50),  nullable=True)
    observacoes        = db.Column(db.Text,        nullable=True)
    foto_base64        = db.Column(db.Text,        nullable=True)
    foto_mime          = db.Column(db.String(50),  nullable=True)
    foto_nome          = db.Column(db.String(200), nullable=True)
    cv_base64          = db.Column(db.Text,        nullable=True)
    cv_mime            = db.Column(db.String(50),  nullable=True)
    cv_nome            = db.Column(db.String(200), nullable=True)
    template_escolhido = db.Column(db.String(20),  nullable=True)
    pago               = db.Column(db.Boolean,     default=False)
    pagamento_id       = db.Column(db.String(150), nullable=True)
    pdf_path           = db.Column(db.String(300), nullable=True)
    criado_em          = db.Column(db.DateTime,    default=datetime.utcnow)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    try:
        d = request.get_json(force=True)

        curriculo = Curriculo(
            protocolo      = d.get('protocolo', ''),
            tipo           = d.get('tipo', ''),
            nome           = d.get('nome', ''),
            email          = d.get('email', ''),
            telefone       = d.get('telefone', ''),
            idade          = d.get('idade', ''),
            cidade         = d.get('cidade', ''),
            estado         = d.get('estado', ''),
            linkedin       = d.get('linkedin', ''),
            pretensao      = d.get('pretensao', ''),
            objetivo       = d.get('objetivo', ''),
            escolaridade   = d.get('escolaridade', ''),
            curso_grad     = d.get('curso_grad', ''),
            instituicao    = d.get('instituicao', ''),
            ano_conclusao  = d.get('ano_conclusao', ''),
            hard_skills    = d.get('hard_skills', ''),
            soft_skills    = d.get('soft_skills', ''),
            certificacoes  = d.get('certificacoes', ''),
            projetos       = d.get('projetos', ''),
            experiencia    = d.get('experiencia', ''),
            observacoes    = d.get('observacoes', ''),
            foto_base64    = d.get('fotoBase64', ''),
            foto_mime      = d.get('fotoMime', ''),
            foto_nome      = d.get('fotoNome', ''),
            cv_base64      = d.get('cvBase64', ''),
            cv_mime        = d.get('cvMime', ''),
            cv_nome        = d.get('cvNome', ''),
        )

        db.session.add(curriculo)
        db.session.commit()

        return jsonify({'success': True, 'usuario_id': curriculo.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/escolher-template/<int:cid>', methods=['POST'])
def escolher_template(cid):
    c = Curriculo.query.get_or_404(cid)
    c.template_escolhido = request.get_json().get('template', 'curto')
    db.session.commit()
    return jsonify({'success': True})


@app.route('/preview/<int:cid>')
def preview(cid):
    c = Curriculo.query.get_or_404(cid)
    template = request.args.get('template', c.template_escolhido or 'curto')
    c.template_escolhido = template
    db.session.commit()
    return render_template(f'curriculo_{template}.html', c=c)


@app.route('/pagar/<int:cid>', methods=['POST'])
def pagar(cid):
    c = Curriculo.query.get_or_404(cid)
    # ── Aqui você integra o Mercado Pago depois ──
    # Por agora retorna mock para testes
    return jsonify({
        'success': True,
        'url_pagamento': f'/pagamento/mock/{cid}',
        'valor': 19.90
    })


# Rota de teste de pagamento (remover em produção)
@app.route('/pagamento/mock/<int:cid>')
def pagamento_mock(cid):
    c = Curriculo.query.get_or_404(cid)
    c.pago = True
    c.pagamento_id = f'MOCK_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    db.session.commit()
    pdf_path = gerar_pdf(c)
    return f'''
    <html><body style="font-family:sans-serif;text-align:center;padding:60px;">
        <h2 style="color:#16A34A;">✅ Pagamento confirmado!</h2>
        <p>Seu currículo foi gerado com sucesso.</p>
        <a href="/download/{cid}" style="display:inline-block;margin-top:20px;padding:14px 32px;
           background:#2A6DD9;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;">
           ⬇️ Baixar Currículo PDF
        </a>
    </body></html>
    '''


@app.route('/webhook/pagamento', methods=['POST'])
def webhook_pagamento():
    data = request.get_json(silent=True) or {}
    if data.get('action') == 'payment.completed':
        cid = data.get('metadata', {}).get('curriculo_id')
        if cid:
            c = Curriculo.query.get(cid)
            if c:
                c.pago = True
                c.pagamento_id = data.get('collection_id', '')
                db.session.commit()
                gerar_pdf(c)
    return '', 200


@app.route('/check-pagamento/<int:cid>')
def check_pagamento(cid):
    c = Curriculo.query.get_or_404(cid)
    return jsonify({'pago': c.pago})


@app.route('/download/<int:cid>')
def download(cid):
    c = Curriculo.query.get_or_404(cid)
    if not c.pago:
        return jsonify({'error': 'Pagamento necessário'}), 403
    if not c.pdf_path or not os.path.exists(c.pdf_path):
        # Tentar gerar novamente
        path = gerar_pdf(c)
        if not path:
            return jsonify({'error': 'PDF não encontrado'}), 404
    nome_arquivo = f"curriculo_{c.nome.replace(' ', '_')}.pdf"
    return send_file(c.pdf_path, as_attachment=True, download_name=nome_arquivo)


def gerar_pdf(curriculo):
    """Gera PDF usando weasyprint — pip install weasyprint"""
    try:
        from weasyprint import HTML
        template = curriculo.template_escolhido or 'curto'
        html_str = render_template(f'curriculo_{template}.html', c=curriculo)
        path = f'output/curriculo_{curriculo.id}.pdf'
        HTML(string=html_str).write_pdf(path)
        curriculo.pdf_path = path
        db.session.commit()
        return path
    except ImportError:
        print("⚠️  weasyprint não instalado. Execute: pip install weasyprint")
        return None
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return None


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("\n🚀 Servidor iniciado!")
    print("📍 Acesse: http://localhost:5000")
    print("💾 Banco:  curriculos.db\n")
    app.run(debug=True, host='0.0.0.0', port=5000)