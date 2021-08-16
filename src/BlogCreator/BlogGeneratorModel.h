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
#ifndef BLOGGENERATORMODEL_H
#define BLOGGENERATORMODEL_H

#include <QNetworkAccessManager>
#include <QObject>

class BlogGeneratorModel : public QObject
{
    Q_OBJECT
public:
    explicit BlogGeneratorModel(QObject *parent = nullptr);

    Q_INVOKABLE
    void generateText(const QString &prefix, int minTextLength=-1, int maxTextLength=-1);

signals:
    void textGenerationFinished(const QString &newText);

private:
    QNetworkAccessManager *m_accessManager;
};

#endif // BLOGGENERATORMODEL_H
