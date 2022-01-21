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
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>

#include "BlogGeneratorModel.h"
#include "PythonEnv.h"

int main(int argc, char *argv[])
{
    // Python lifetime guard
    py::scoped_interpreter guard{};

    // Set custom sys path
    py::module sys = py::module::import("sys");
    py::handle sys_path = sys.attr("path");
    //sys_path.attr("clear")();
    //sys_path.attr("append")("");
    sys_path.attr("append")("~/anaconda3/lib/python38.zip");
    sys_path.attr("append")("~/anaconda3/lib/python3.8");
    sys_path.attr("append")("~/anaconda3/lib/python3.8/lib-dynload");
    sys_path.attr("append")("~/anaconda3/lib/python3.8/site-packages");


#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
#endif

    QGuiApplication app(argc, argv);

    // Register custom styles
    qmlRegisterType<BlogGeneratorModel>("BlogCreator.BlogGeneratorModel", 1, 0, "BlogGeneratorModel");

    // Activate the styling
    QQuickStyle::setStyle("Material");

    QQmlApplicationEngine engine;
    const QUrl url(QStringLiteral("qrc:/main.qml"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                     &app, [url](QObject *obj, const QUrl &objUrl) {
        if (!obj && url == objUrl)
            QCoreApplication::exit(-1);
    }, Qt::QueuedConnection);
    engine.load(url);

    return app.exec();
}
