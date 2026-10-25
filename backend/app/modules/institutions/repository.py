def assigned_institutions(db, scope):
    return db.obligations.distinct('institution_id', scope)


def page(db, query, limit, offset):
    return list(db.institutions.find(query).sort('_id', 1).skip(offset).limit(limit)), db.institutions.count_documents(query)
