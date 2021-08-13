// Copyright (C) 2021 Jan Tschada (gisfromscratch@live.de)
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
// Additional permission under GNU GPL version 3 section 7
//
// If you modify this Program, or any covered work, by linking or combining
// it with ArcGIS Runtime for Qt (or a modified version of that library),
// containing parts covered by the terms of ArcGIS Runtime for Qt,
// the licensors of this Program grant you additional permission to convey the resulting work.
// See <https://developers.arcgis.com/qt/> for further information.
//
#include "BlogGeneratorModel.h"

#include <QNetworkReply>

#include "PythonEnv.h"

BlogGeneratorModel::BlogGeneratorModel(QObject *parent) : QObject(parent), m_accessManager(new QNetworkAccessManager(this))
{

}

void BlogGeneratorModel::generateText(const QString &prefix)
{
    QUrl url(QString("http://127.0.0.1:5000/prefix=%1").arg(prefix));
    QNetworkRequest textRequest(url);
    QNetworkReply *textReply = m_accessManager->get(textRequest);
    connect(textReply, &QNetworkReply::finished, [this, textReply]()
    {
        switch (textReply->error())
        {
        case QNetworkReply::NetworkError::NoError:
            break;

        default:
            qCritical() << textReply->errorString();
            return;
        }

        QString text = textReply->readAll();
        emit textGenerationFinished(text);
    });

    /*
    auto prefixText = prefix.toStdString();
    auto locals = py::dict("name"_a="World", "number"_a=42);
    py::exec(R"(
        import sys
        import numpy
        #from transformers import GPTNeoForCausalLM, GPT2Tokenizer
        #message = "Hello, {name}! The answer is {number}".format(**locals())
        message = "|".join(sys.path)
        message += "|" + sys.executable
    )", py::globals(), locals);

    auto message = locals["message"].cast<std::string>();
    return QString::fromStdString(message);
    */
}
