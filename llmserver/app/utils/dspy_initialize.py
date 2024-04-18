import dspy


def check_dspy(app):
    print("Middleware: Checking dspy configuration")

    if not dspy.settings.lm:
        print("\033[91m Setting up dspy configuration \033[0m")
        turbo = dspy.OpenAI(model="gpt-3.5-turbo")
        colbertv2_wiki17_abstracts = dspy.ColBERTv2(
            url="http://20.102.90.50:2017/wiki17_abstracts"
        )
        dspy.settings.configure(lm=turbo, rm=colbertv2_wiki17_abstracts)
    else:
        print("\033[92m dspy configuration already set \033[0m")

    return app
