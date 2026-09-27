from app.db.models import AspectSentiment, Document
from app.db.session import SessionLocal
from app.nlp.aspect_sentiment import extract_aspects

COMMIT_EVERY = 20  # save progress periodically so a crash partway through does not lose completed work


def main() -> None:
    session = SessionLocal()

    # resumable: skip documents that already have at least one row, so rerunning
    # after a crash does not re-pay for and redo work that already succeeded
    already_processed = {row[0] for row in session.query(AspectSentiment.document_id).distinct().all()}
    documents = [
        d for d in session.query(Document).order_by(Document.id).all()
        if d.id not in already_processed
    ]

    if already_processed:
        print(f"resuming: skipping {len(already_processed)} already-processed documents")

    total_mentions = 0
    for i, document in enumerate(documents, start=1):
        mentions = extract_aspects(document.text)

        for mention in mentions:
            session.add(AspectSentiment(
                document_id=document.id,
                product_id=document.product_id,
                aspect=mention.aspect,
                sentiment=mention.sentiment,
                quote=mention.quote,
            ))
        total_mentions += len(mentions)

        if i % COMMIT_EVERY == 0:
            session.commit()
            print(f"{i}/{len(documents)} documents processed, {total_mentions} mentions so far")

    session.commit()  # save whatever is left after the loop
    session.close()

    print(f"done. {len(documents)} documents processed this run, {total_mentions} aspect mentions extracted")


if __name__ == "__main__":
    main()
